var standard_size=10;
var max_size=30;
var fill_color="rgba(0,128,128,0.5)";
var stroke_color="#000000";
var stroke_width=1;
var max_displacement=50;
function standard_func(id){
	console.log(id);
}




PlaneVisualizer=function(div_id,width, height, kwargs){
	this.svg=document.getElementById(div_id);	
	this.points={};
	this.width=width;
	this.height=height;
	var rect= document.createElementNS("http://www.w3.org/2000/svg", "rect");

	rect.setAttribute("x",0);
	rect.setAttribute("y",0);
	rect.setAttribute("height",this.height);
	rect.setAttribute("width",this.width);


	rect.setAttribute("stroke","#000");
	rect.setAttribute("fill","#FFF");
	this.svg.appendChild(rect);
	this.omv_=this.omv.bind(this);
	this.svg.onmousemove=this.omv_;
	this.clk_=this.clk.bind(this);
	this.svg.onclick=this.clk_;


	this.lens={'radius': 50};

	this.mouse= document.createElementNS("http://www.w3.org/2000/svg", "circle");
	this.mouse.setAttribute("fill","rgba(200,255,255,0.8)");
	this.mouse.setAttribute("r",this.lens.radius*2);
	this.svg.appendChild(this.mouse)
}	

PlaneVisualizer.prototype = {
	omv: function(event) {
		var x=event.offsetX;
		var y=event.offsetY;
		this.mouse.setAttribute("cx",x);
		this.mouse.setAttribute("cy",y);
		var ok=Object.keys(this.points);
		for(var p=0; p<ok.length; p++){
			var point=this.points[ok[p]];
			var dists=point.computeDist(x,y);
			point.size=point.standard_size;
			point.x=point.x_c;
			point.y=point.y_c;
			if(dists[2]<this.lens.radius){
				point.size=point.standard_size+(point.max_size-point.standard_size)*(1-dists[2]/this.lens.radius);
				if(dists[2]>0)
				{
					var displ=max_displacement*Math.sin(dists[2]/this.lens.radius*Math.PI);
					point.x=point.x_c+displ*dists[0]/dists[2];
					point.y=point.y_c+displ*dists[1]/dists[2];				
				}
			}		
			point.move();
		}
		
	},
	clk:function(event){		
		var x=event.offsetX;
		var y=event.offsetY;
		var minpoint=null;
		var mindist=this.width+this.height;
		var ok=Object.keys(this.points);
		for(var p=0; p<ok.length; p++){
			var point=this.points[ok[p]];
			var dists=point.computeDist(x,y);
			if(dists[2]<mindist){
				minpoint=point;
				mindist=dists[2];
			}			
		}
		if(mindist<minpoint.size){
			minpoint.func(minpoint.id);
		}
	},

	loadPoints: function(filename) {
		; //adding points from a remotefile
	},
	addPoints: function(points){
		for(var p=0; p<points.length; p++){
			var point=points[p];			
			point.set_pv(this);
			point.recenter(point.x_c*this.width, point.y_c*this.height);
			point.insert();
			this.points[point.id]=point;
			
		}
	},
	drawPoints: function(){
		for (var p=0; p<this.points.length; p++){
			this.points[p].draw();
		}
	}
}




Point=function(x_c,y_c,id, kwargs){
	this.x_c=x_c;
	this.y_c=y_c;
	this.pv=null
	this.id=id;
	this.x=this.x_c;
	this.y=this.y_c;
	this.standard_size=standard_size;
	this.div= document.createElementNS("http://www.w3.org/2000/svg", "circle");
	this.div.setAttribute("id", id);
	
	this.size=this.standard_size;
	this.max_size=max_size;
	this.fill_color=fill_color;
	this.stroke_color=stroke_color;
	this.stroke_width=stroke_width;
	this.func=standard_func;

	if(kwargs===undefined){return}
	
	if (kwargs["standard_size"] !==undefined){
		this.standard_size=kwargs["standard_size"];
	}
	if (kwargs["max_size"] !==undefined){
		this.max_size=kwargs["max_size"];
	}
	
	if (kwargs["fill_color"] !==undefined){
		this.fill_color=kwargs["fill_color"];
	}	

	
	if (kwargs["stroke_color"] !==undefined){
		this.stroke_color=kwargs["stroke_color"];
	}	

	
	if (kwargs["stroke_width"] !==undefined){
		this.stroke_width=kwargs["stroke_width"];
	}

	
	if (kwargs["func"] !==undefined){
		this.func=kwargs["func"];
	}		
}
Point.prototype = {
	recenter: function(cx, cy) {
		this.x_c=cx;
		this.y_c=cy;
		this.x=cx;
		this.y=cy;
	},
	set_pv: function(pv) {
		this.pv=pv;
	},
	computeDist: function(x,y) {
		var distx=this.x_c-x;
		var disty=this.y_c-y;
		var dist=Math.sqrt(Math.pow(distx,2)+Math.pow(disty,2));
		return [distx, disty, dist]
	},
	insert: function(){

		this.div.setAttribute("cx",Math.round(this.x_c));
		this.div.setAttribute("cy",Math.round(this.y_c));
		this.div.setAttribute("r",this.standard_size);
		this.div.setAttribute("stroke",this.stroke_color);
		this.div.setAttribute("stroke-width",this.stroke_width);
		this.div.setAttribute("fill",this.fill_color);
		
		this.pv.svg.appendChild(this.div);
	},
	move: function(){
		this.div.setAttribute("cx",Math.round(this.x));
		this.div.setAttribute("cy",Math.round(this.y));
		this.div.setAttribute("r",this.size);		
	}

}