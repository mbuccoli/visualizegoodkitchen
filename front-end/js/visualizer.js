var points=[]
var PV=null;

function main(){
	for (var p=0; p<points_json.length; p++){
		var point=points_json[p];
		points.push(new Point(point[0],point[1],point[2]));
	}
	PV=new PlaneVisualizer("plane",800,600);
	PV.addPoints(points);
}