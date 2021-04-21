// Aspect ratios must be the same
mapHeight = 500
mapWidth = 1000
viewHeight = 500
viewWidth = 1000

viewScale = 1

    
function ConvertCartesianToHTMLCoordiantes(center, point) {
    return new Point(point.x, center.y - point.y)
}

function toViewScale(meters) {
    return meters * viewScale
}

window.onload = function() {
	paper.setup('map');
	with (paper) {
		var path = new Path();
		path.strokeColor = 'black';
		var start = new Point(100, 100);
		path.moveTo(start);
		path.lineTo(start.add([ 200, -50 ]));
		view.draw();

        
		var tool = new Tool();

		// Define a mousedown and mousedrag handler
		tool.onMouseDown = function(event) {
			path = new Path();
			path.strokeColor = 'black';
			path.add(event.point);
		}

		tool.onMouseDrag = function(event) {
			path.add(event.point);
		}
	}
}