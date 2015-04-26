/* constants */
var MOVE_BY = [
	5, 	// [0] normal
	30,	// [1] fast with shift
	2  	// [2] slow with ctrl
];

var ZOOM_NORM = 1;
var ZOOM_HALF = 0.5;
var ZOOM_QUAR = 0.25;
var SIG_UPD_INTERVAL = 1000;

/* so called global variables */
var contSize; // stores dimensions of #main div container
var posX, posY; // store current position - where viewfinder aims
var fplanSize; // store floorplan size
var sPoints; // store survey points ( array )
var zoom; // store current zoom
var hmapRdy; // is heatmap ready
var setApPos = 0; // set to 1 when user is setting ap position ( toggle )
var apPosX; // stores X AP position 
var apPosY; // stores Y AP position
var apPosSet; // whether AP has been placed

/* SurveyPoint class */
function SurveyPoint(name,posX,posY,signalSta) {
	this.name = name;
	this.posX = posX;
	this.posY = posY;
	this.signalSta = signalSta;	
}

/* function set up environment, called on document ready */
function init() {
    zoom = ZOOM_NORM;
	appendToLogLine("-----( wcml webapp surveying tool started)-----");
	contSize = getMainContainerSize();
    console.log(contSize);
	posX = Math.floor(contSize['width']/2);
	posY = Math.floor(contSize['height']/2);
	fplanSize = getFloorplanSize();
	// set floorplan from JS 
	$("#fplan").css("background-image","url('"+fplanImgUrl+"')");
    // ugly hack to get background-position-* available
	$("#fplan").css("background-position-x","0px");
	$("#fplan").css("background-position-y","0px");
	$("#heatmap").css("background-position-x","0px");
	$("#heatmap").css("background-position-y","0px");
	$("#sample-map").css("top","0px");
	$("#sample-map").css("left","0px");
    $("#ap-layer").css("top","0px");
    $("#ap-layer").css("left","0px");

	sPoints = [];
	appendToLog("Retrieving saved points ...");
    $.getJSON("retrieve_survey_points.json", function(data) {
	   for ( var i = 0, len = data.points.length; i < len; i++ ) {
		curS = data.points[i];
        	sPoints.push(new SurveyPoint(curS['name'],curS['pos_x'],curS['pos_y'],curS['signal_sta'])); // add point to collection
			domAddPoint(curS['name'],curS['signal_sta']);
        }
        drawMapViews(); // called here because request must finish
		appendToLogLine(" done");
    });
	checkFloorplanSize();
    getApPosition();
	checkHmapReady();
	populateSignalChart();

	// activate buttons
	$("#btn-reset").click(function() {
		_reset_survey();
	});

	$("#btn-gen-hmap").click(function() {
		_generate_heatmap();
	});
    
    $("#btn-place-ap").click(function() {
	   _place_ap();
    });
    $("#btn-gen-deliv").click(function() {
	   _generate_deliverables();
    });
    
    $("#ctrl-hmap-vis").change(function() {
        var val = $(this).val();
        $("#heatmap").css("opacity",val/100.0);
    });

	$("#color-red").click(function() {
		console.log("red");
		$("#viewfinder").css("background-image","url('../static/images/viewfinder-red.png')");
	});

    $("#color-green").click(function() {
		console.log("green");
		$("#viewfinder").css("background-image","url('../static/images/viewfinder-green.png')");
	});
    
    $("#color-blue").click(function() {
		$("#viewfinder").css("background-image","url('../static/images/viewfinder-blue.png')");
	});
}

function _place_ap() {
    appendToLog("Setting AP position... ");
	saveApPosition();
	domAddAp();
	drawMapViews();
    setApPos = 1;
}

function _reset_survey() {
	appendToLog('Resetting in 1 sec.');
	$.get("reset_survey");
	setTimeout(location.reload(),1000);

}

function _generate_heatmap() {
	$("#heatmap").css("background-image",'none');
	appendToLog("Generating heatmap ....");
	$.get("generate_heatmap", function(data)  {
		if ( data = "OK" ) {
			appendToLogLine(" succeeded.");
			checkHmapReady();
		}
		else {
			appendToLogLine(" failed.");
		}
	});

}

function _generate_deliverables() {
	$.get("generate_deliverables", function(data) {
		$("#deliv-link").empty();
		$("#deliv-link").append("[<a href=\"../static/deliverables/"+data+".zip\">download</a>]");
	});
}

function appendToLog(msg) {
	appendToLogLine("\r\n"+msg);
}

function appendToLogLine(msg) {
	var old_val = $("#event-log").text();
	$("#event-log").text(old_val+msg);
	$("#event-log")[0].scrollTop = $("#event-log")[0].scrollHeight;
}

/* return size of the loaded floorplan image */
function getFloorplanSize() {
	var fplanSize = new Object();
	
	var tmpImg = new Image();
	tmpImg.src = fplanImgUrl;
    // gets natural image size after it's loaded
	$(tmpImg).load(function() {
		fplanSize['height']=tmpImg.naturalHeight;
		fplanSize['width']=tmpImg.naturalWidth;
	});
	return fplanSize;
}

function getApPosition() {
    /** Check if AP position has been saved. If so retrieve it to JS app
    */
    $.get("get_surv_set/1/ap_set", function(data) {
		
        if ( data == 'true' ) {
			appendToLog('AP position set');
            apPosSet = 1;
            $.get("get_surv_set/1/ap_pos_x", function(data) {
                apPosX = data;
                drawMapViews(); // request completed, now it's time to refresh view
            });
            $.get("get_surv_set/1/ap_pos_y", function(data) {
                apPosY = data;
                drawMapViews(); // request completed, now it's time to refresh view
            });
            domAddAp();
            drawMapViews(); // request completed, now it's time to refresh view
			
        }
    });
    
}

function checkHmapReady() {
	/** Check in DB is heatmap ready, if so it sets heatmap
	 * layer visible. Called from init()  */
	$.get("get_surv_set/1/hm_retr", function(data) {
        if ( data == 'true' ) {
			appendToLog('Heatmap already retrieved - showing');
			setHmapVisible(true);
        }
    });
}

function setHmapVisible(visible) {
	if ( visible ) {
		var d = new Date(); // 'random' value added to URL avoids caching by browser
		$("#heatmap").css("background-image","url('../static/images/hmap.png?"+d.getTime()+"')");
	} else {
		$("#heatmap").css('background-image','none');
	}
}

/* saveFloorplanSize() saves floorplan size if it's not in db yet */
function checkFloorplanSize() {
	$.get("get_surv_set/1/fplan_dim_set", function(data) {
		if ( data == 'false' ) {
			$.get("set_surv_set/1/fplan_width/"+fplanSize['width']);
			$.get("set_surv_set/1/fplan_height/"+fplanSize['height']);
			$.get("set_surv_set/1/fplan_dim_set/true");
		}
	});
}


function populateSignalChart() {
	for ( var i=0; i < 20; i++ ) {
		$("#sig-chart").append("<div class=\"sig-chart-bar\">" +
			"<div class=\"sig-chart-bar-hide\"" +
			"style=\"height: 140px;\"></div></div>");
	}
}

function updateSignalChart(signal) {
	// remove oldest ( first ) sample
	$("#sig-chart .sig-chart-bar").last().remove();
	// filter out outstanding values
	if ( signal < -100 ) {
		signal = -100;
	}
	if ( signal > -30 ) {
		signal = -30
	}
	// apply color
	var color = "";
	if ( signal > -60 ) {
		color = "#00E000";
	} else if ( signal > -67 ) {
		color = "#B8F024";
	} else if ( signal > -74 ) {
		color = "#FFBD00";
	} else {
		color ="#CC330D";
	}

	var hiderHeight = Math.abs(signal+30)*2;
	$("#sig-chart").prepend("<div class=\"sig-chart-bar\" style=\"background-color:" +
		color + ";\"><div class=\"sig-chart-bar-hide\" style=\"height: " + hiderHeight +
		"\"></div></div>");
}

/* return size of #main container, called once page is loaded and on each 
 * window resize */
function getMainContainerSize() {
	console.log("getMainContainerSize() start");
	var contSize = new Object();
	contSize['width'] = $("#main").width();
	contSize['height'] = $("#main").height();
	console.log("getMainContainerSize() end");
	return contSize;
}

function handleMove(dir,mode) {
	if ( dir == "up" ) {
		// near top edge
		if ( posY - MOVE_BY[mode] < 0 ) {
			posY = 0;
		} else {
			posY -= MOVE_BY[mode];
		}
	}	

	if ( dir == "down" ) {
		// near bottom edge
		if ( posY + MOVE_BY[mode] > fplanSize['height']  ) {
			posY = fplanSize['height']; 
		} else {
			posY += MOVE_BY[mode];
		}
	}	

	if ( dir == "right" ) {
		// near right edge
		if ( posX + MOVE_BY[mode] > fplanSize['width']  ) {
			posX = fplanSize['width'];
		} else {
			posX += MOVE_BY[mode];
		}
	}	

	if ( dir == "left" ) {
		// near left edge
		if ( posX - MOVE_BY[mode] < 0  ) {
			posX = 0;
		} else {
			posX -= MOVE_BY[mode];
		}
	}	
	// refresh view
	drawMapViews();
}

function drawMapViews() {
	console.log("drawMapViews() start");
	// hide samples and ap while it's being draw
	$("#sample-map").css("visibility","hidden");
	$("#ap-layer").css("visibility","hidden");

	// zoom awareness
	var vFplanHeight = Math.floor(fplanSize['height']*zoom);
	var vFplanWidth = Math.floor(fplanSize['width']*zoom);

	// scale floorplan
	$("#fplan").css("background-size",vFplanWidth+"px "+vFplanHeight+"px");
	$("#heatmap").css("background-size",vFplanWidth+"px "+vFplanHeight+"px");

	// calculate shift
	var shiftX = Math.floor(contSize['width']/2) - Math.floor(posX*zoom);
	var shiftY = Math.floor(contSize['height']/2) - Math.floor(posY*zoom); 

	// apply shift
	$("#fplan").css("background-position-x",shiftX+"px");
	$("#fplan").css("background-position-y",shiftY+"px");
	$("#heatmap").css("background-position-x",shiftX+"px");
	$("#heatmap").css("background-position-y",shiftY+"px");
	$("#sample-map").css("left",shiftX+"px");
	$("#sample-map").css("top",shiftY+"px");
	$("#ap-layer").css("left",shiftX+"px");
	$("#ap-layer").css("top",shiftY+"px");




	// clip sample map to avoid visible samples outside of view area
	// clip syntax is rect(top,right,bottom,left)
	var viewAreaWidth = 0;
	var viewAreaHeight = 0;
	if ( ( vFplanWidth + shiftX ) > contSize['width'] ) {
		viewAreaWidth = contSize['width'];
	} else {
		viewAreaWidth = vFplanWidth + shiftX;
	}
	if ( ( vFplanHeight + shiftY ) > contSize['height'] ) {
		viewAreaHeight = contSize['height'];	
	} else {
		viewAreaHeight = vFplanHeight + shiftY;
	}
	// assign starting clipping values
	var clipTop = 0;
	var clipRight = viewAreaWidth;
	var clipBottom = viewAreaHeight ;
	var clipLeft = 0;

	// modify clipping according to viewable area
	if ( shiftX < 0 ) {
		clipLeft = -shiftX;
		clipRight = viewAreaWidth - shiftX;
	} else if ( shiftX > 0 ) {

		clipRight = viewAreaWidth - shiftX;
	}

	if ( shiftY < 0 ) {
		clipTop = -shiftY;
		clipBottom = viewAreaHeight - shiftY;
	} else if ( shiftY > 0 ) {
		clipBottom = viewAreaHeight - shiftY;
	}
	// prepare css syntax and apply
	var cssClipRect = "rect("+clipTop+"px,"+clipRight+"px,"+clipBottom+"px,"+clipLeft+"px)";
	



	
	// draw samples points
	__cur_samples = sPoints.length;
	for ( var i = 0; i < __cur_samples; i++ ) {
		var sName = "#s-"+i;
		$(sName).css("margin-left",Math.floor(sPoints[i].posX*zoom)-8+"px");
		$(sName).css("margin-top",Math.floor(sPoints[i].posY*zoom)-8+"px");

	}
    
    $("#ap-marker").css("margin-left",Math.floor(apPosX*zoom)-8+"px");
    $("#ap-marker").css("margin-top",Math.floor(apPosY*zoom)-8+"px");

    $("#sample-map").css("clip",cssClipRect);
	// show samples and ap when it's done
	$("#sample-map").css("visibility","visible");
	$("#ap-layer").css("visibility","visible");

	console.log("drawMapViews() end");
}

function domAddPoint(name,sig) {
	/* Iplements DOM manipulation when adding point. Inserts
	 * new <div> to #sample-map */
	$("#sample-map").append("<div class=\"sample\" id=\""+name+"\" alt=\""+sig+"\" title=\""+sig+"\">"+sig+"</div>");
}
function domAddAp() {
	$("#ap-layer").empty();
    $("#ap-layer").append("<div id=\"ap-marker\">AP</div>");
}


function saveApPosition() {
    /* Saves AP position. Performs request via get requests which
    saves posititon in db. */
    $.get("set_surv_set/1/ap_pos_x/"+posX);
    $.get("set_surv_set/1/ap_pos_y/"+posY);
    $.get("set_surv_set/1/ap_set/true");
    apPosX = posX;
    apPosY = posY;
    appendToLog("saved.");
    //drawMapViews();
    
}

function addPoint() {
    /* addPoint() add point on the map with current position and signal level.
     * Sginal level is obtained through AJAX request, point is added to in-memory
     * collection, point is added to the map and finally AJAX request is made to
     * store it in DB */
    var _signal_val = -200; // known bad value
    
    $.get("get_signal", function( data ) {
        _signal_val = parseInt( data ); // store retrieved value
        _cur_length = sPoints.length; // amount of sample points
        var sName = "s-"+_cur_length; // prepare name
        sPoints.push(new SurveyPoint(sName,posX,posY,_signal_val)); // add point to collection
        //console.log('adding point: '+sName+',posx:'+posX+',posy:'+posY+",rssi:"+_rssi_val);
		domAddPoint(sName,_signal_val);
	$("#"+sName).css("visibility","hidden");
	// perform ajax request storing point in db
        $.ajax({
            //url: "http://127.0.0.1:8000/test2_survapp/default/call/jsonrpc",
            url: "call/jsonrpc",
            data: JSON.stringify({method:"save_point",params:[sName,posX,posY,_signal_val],id:"jsonrpc"}),
            type: "POST",
            dataType:"json",
            success: function ( result ) {
		drawMapViews();
            },
            error: function(err,status,thrown) {
                console.log('error');
		$("#"+sName).css("visibility","visible");
            },
            complete: function(xhr,status) {
		$("#"+sName).css("visibility","visible");
		drawMapViews();
            }

        });
        console.log(data);
    });
	
	
    
}

function changeZoom() {
	switch ( zoom ) {
		case ZOOM_NORM:
			zoom = ZOOM_HALF;
			break;
		case ZOOM_HALF:
			zoom = ZOOM_QUAR;
			break;
		case ZOOM_QUAR:
			zoom = ZOOM_NORM;
			break;
	}
	drawMapViews();
}

$( window ).load(function() {
	// detect and handle window resizing
	$( window ).resize(function() {
		console.log("window resized");
	});

	init();

    // polling of signal value
    (function poll() {
        setTimeout(function() {
            $.ajax({ url: "get_signal", success: function(data) {
                $("#signal").text(data+" dBm");
                updateSignalChart(parseInt(data));
            }, complete: poll });
        }, SIG_UPD_INTERVAL);
    })();
	// keyboard handling
	$(document).keydown(function(e) {
		/* shift and control are speed modifiers, modes:
		0 - normal speed
		1 - fast speed ( with shift )
		2 - slow speed ( with control ) */
		var mode = 0;
        // set mode according to pressed modifiers ctrl / shift
		if ( e.shiftKey ) {
			mode = 1;
		}
		if ( e.ctrlKey ) {
			mode = 2;
		}
        // normal mode if both ctrt / shift are pressed
		if ( e.shiftKey && e.ctrlKey ) {
			mode = 0;
			//console.log("MODE NORMAL");
		}
		// j or arrow down - move down
		if ( e.which == 74 || e.which == 40 ) {
			handleMove("down",mode);
		}
		// k or arrow up - move up
		if ( e.which == 75 || e.which == 38 ) {
			handleMove("up",mode);
		}
		// h or arrow left - move left
		if ( e.which == 72 || e.which == 37 ) {
			handleMove("left",mode);
		}

		// l or arrow right - move right
		if ( e.which == 76 || e.which == 39 ) {
			handleMove("right",mode);
		}

		// i or enter - add point 
		if ( e.which == 73 || e.which == 13 ) {
            addPoint();
			drawMapViews();
        }

		// z - change zoom
		if ( e.which == 90 ) {
			changeZoom();
		}
        
        // v - change heatmap opacity
        if ( e.which == 86 ) {
            curOp = $("#heatmap").css("opacity");
            if ( mode == 1 ) {
                // increases opacity
                newOp = parseFloat(curOp)+0.05;
                $("#heatmap").css("opacity",newOp);
                $("#ctrl-hmap-vis").val(Math.floor(newOp*100));            
            } else {
                newOp = parseFloat(curOp)-0.05;
                $("#heatmap").css("opacity",newOp);
                $("#ctrl-hmap-vis").val(Math.floor(newOp*100));
            }
        }

        if ( e.which == 82 ) {
            _reset_survey();
        }
        if ( e.which == 65 ) {
            _place_ap();
        }
        if ( e.which == 71 ) {
            _generate_heatmap();
        }
		// prevents browser shortcuts to be triggered
		e.preventDefault();
	});
	
});
