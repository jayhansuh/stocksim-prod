class d3graph {
    constructor(svg,strt_date){
        this.svg = svg;
        this.data = [];//[{'date': - , 'asset': - ,'Open': - , 'Close': - , 'MA': - ,},...]
        this.player = {'asset':1000.,'pos':0};
        this.max_pos = 2;
        this.min_pos = -1;

        this.inputdata_que=[];
        this.inputdata_PID=0;

        this.height = 500;
        this.width = 700;
        this.margin = {top: 20, right: 30, bottom: 30, left: 40};

        this.gridcolor="rgb(255,165,0)";
        this.y1color="rgb(155,165,200)";
        this.y2color="rgb(194,180,200)";
        
        this.candleobj = null;
        this.xscale = null;
        this.yscale = null;
        this.yanchor = null;
        this.line = null;
        this.area = null;

        this.plot_index = 0;
        this.plot_index_f = 0;
        this.strt_date = strt_date;
        this.movingavgdays=25;
        this.sum_arr = [];
        this.last_close = null;

        this.ANIM_INTERVAL=300;
        this.PLAY_INTERVAL=301;
    }
    
    draw(){

        const data = this.data.slice(this.plot_index)
        const height = this.height;
        const width = this.width;
        const margin = this.margin;
        const svg = this.svg;

        // set and draw x axis
        this.xscale = d3.scaleLinear()
            .domain([data[0].dateind, data[data.length - 1].dateind])
            .range([margin.left, width - margin.right]);

        svg.append("g")
        .attr('class','xaxis')
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .attr('stroke', this.y1color )
        .style('font-size',12)
        .call(
            d3.axisBottom()
            .scale(this.xscale)
            //.tickFormat( i => indtodate(i).slice(5)))
            .tickFormat( i => indtodate(i)))
        //.call(g => g.select(".domain").remove())
        .call(g => g.select(".domain")
            .attr('stroke', this.y1color )
            .attr('opacity', 0.2 ))
        .call(g => g.selectAll("line")
            .attr('stroke', this.y1color )
            .attr('opacity', 0.2 )
            .attr('y1',margin.top + margin.bottom -height ));
        
        // set and draw y axis
        this.yscale = d3.scaleLog()
            .domain([0.95*d3.min(data, d => Math.min(d.Low,d.MA)), 1.05*d3.max(data, d => Math.max(d.High,d.MA))])
            .rangeRound([height - margin.bottom, margin.top])

        svg.append("g")
        .attr('class','yaxis')
        .attr("transform", `translate(${margin.left},0)`)
        .attr('stroke', this.gridcolor)
        .style('font-size',12)
        .call(d3.axisLeft(this.yscale)
            .tickFormat(numformat)
            .tickValues(d3.scaleLinear().domain(this.yscale.domain()).ticks()))
        .call(g => g.selectAll(".tick line").clone()
            .attr('class','hline')
            .attr('stroke',this.gridcolor)
            .attr("stroke-opacity", 0.2)
            .attr("x2", width - margin.left - margin.right))
        .call(g => g.select(".domain").style('opacity','0'));

        // set and draw y2 axis
        if(graph.y2color){
            this.yscale2 = d3.scaleLinear()
            .domain(
                //[Math.min(700,0.9*d3.min(data, d => d.asset)), Math.max(1.1*d3.max(data, d => d.asset),2000)]
                [Math.min(800,0.9*d3.min(data, d => d.asset)), Math.max(1.1*d3.max(data, d => d.asset),1600)]
            )
            .range([height - margin.bottom, margin.top])

            svg.append("g")
            .attr('class','yaxis2')
            .attr("transform", `translate(${width-margin.right},0)`)
            .attr('stroke', this.y2color)
            .style('font-size',12)
            .call(d3.axisRight(this.yscale2)
                .tickFormat((num)=>{
                    if(num<1000){ return `${Math.floor(num)}` }
                    return `${(num/1000).toFixed(1)}k`
                })
                .tickValues(this.yscale2.ticks()))
            .call(g => g.select(".domain").remove())
            .call(g => g.selectAll("line").attr('stroke',"rgba(194,180,200,0.5)"));
        }

        // drawing tools
        this.line = d3.line()
            .defined(d => !isNaN(d.MA))
            .x(d => this.xscale(d.dateind))
            .y(d => this.yscale(d.MA));
        
        this.area = d3.area()
            .defined(d => !isNaN(d.MA))
            .x((d) => this.xscale(d.dateind) ) 
            .y0((d) => this.yscale(d.MA*1.05) ) 
            .y1((d) => this.yscale(d.MA*0.95) );
        
        this.line2 = d3.line()
            .defined(d => !isNaN(d.asset))
            .x(d => this.xscale(d.dateind))
            .y(d => this.yscale2(d.asset));

        // draw moving average
        const maobj = svg.append("path")
            .datum(data)
            .attr('class','MA')
            .attr("fill", "none")
            .attr("stroke", "steelblue")
            .attr("stroke-width", 1.5)
            .attr("stroke-linejoin", "round")
            .attr("stroke-linecap", "round")
            .attr("transform", `translate(0,0)`)
            .attr("d", this.line);

        // draw moving average envelope
        const maenvobj = svg.append("path")
            .datum(data)
            .attr('class','MAenv')
            .attr("fill", "rgba(165,52,36,0.18)")
            .attr("transform", `translate(0,0)`)
            .attr("d", this.area);  

        // set rounded corner
        const candleobj = svg.append("g")
            //.attr("stroke-linecap", "butt")
            //.attr('class','candlecont');

        this.candleobj = candleobj;

        let newcandle = candleobj
            .selectAll("g")
            .data(data)
            .enter()
            .append('g')
            .attr("transform", (d,i) => `translate(${this.xscale(d.dateind)},0)`);

        // draw High-Low line
        newcandle.append("line")
        .attr('class','HLline')
        .attr("y1", d => this.yscale(d.Low))
        .attr("y2", d => this.yscale(d.High))
        .attr('stroke','gray');

        const stroke_width =(width - margin.right - margin.left)/data.length*0.8;

        // draw candle
        // newcandle.append("line")
        // .attr('class','candle')
        // .attr("y1", d => this.yscale(d.Open))
        // .attr("y2", d => this.yscale(d.Close))
        // .attr("stroke-width", stroke_width)
        // .attr("stroke", d =>
        //     d.Open > d.Close ? "#e41a1c"//d3.schemeSet1[0]
        //     : d.Close > d.Open ? "#4daf4a" //d3.schemeSet1[2]
        //     : "#999999"); //d3.schemeSet1[8]);
        const MIN_CANDLE_HEIGHT = 3;

        newcandle.append("rect")
        .attr('class','candle')
        .attr('rx', 1.5)
        .attr('ry', 1.5)
        .attr('x',-stroke_width/2)
        .attr('width',stroke_width)
        .attr("y", d => Math.min(this.yscale(Math.max(d.Close,d.Open)), this.yscale((d.Close+d.Open)/2) - .5*MIN_CANDLE_HEIGHT))
        .attr("height", d => Math.max(Math.abs(this.yscale(d.Close) - this.yscale(d.Open)) , MIN_CANDLE_HEIGHT ))
        .attr("fill", d =>
            d.Open > d.Close ? "#e41a1c"//d3.schemeSet1[0]
            : d.Close > d.Open ? "#4daf4a" //d3.schemeSet1[2]
            : "#999999"); //d3.schemeSet1[8]);

        // draw asset line
        if(graph.y2color){
            const assetobj = svg.append("path")
                .datum(data)
                .attr('class','asset')
                .attr("fill", "none")
                .attr("stroke", this.y2color )
                .attr("stroke-width", 2.)
                .attr("stroke-linejoin", "round")
                .attr("stroke-linecap", "round")
                .attr("transform", `translate(0,0)`)
                .attr("d", this.line2);
        }
    }

    update(){
        this.svg.selectAll('g').remove()
        this.svg.selectAll('path').remove()
        this.draw()
    }

    appendDatum(datum){
        
        let newdatum = null;

        if(Array.isArray(datum)){
            newdatum = {High:datum[0],Low:datum[1],Open:datum[2],Close:datum[3]};
        }
        else if (typeof(datum)=='object'){
            ['High','Low','Open','Close'].forEach(key => {
                if(!(key in datum)){throw "INVALID DATUM"};
            });
            newdatum = {...datum};
        }
        else {throw "INVALID DATUM"}

        newdatum.dateind = this.strt_date + this.data.length;

        if(newdatum.Close){
            this.last_close=newdatum.Close;
            ['High','Low','Open'].forEach(key =>{
                if(!newdatum[key]){newdatum[key]=this.last_close};
            })
        }
        else{
            if(this.last_close){
                newdatum['High']	= this.last_close;
                newdatum['Low']		= this.last_close;
                newdatum['Open']	= this.last_close;
                newdatum['Close']	= this.last_close;
            }
            else{
                this.strt_date+=1;
                return
            }
        }

        if(this.player.pos==0){
            newdatum['asset']=this.player.asset;
        }
        else{
            let moneyBet = this.player.pos * this.player.asset;
            let moneyCash = this.player.asset - moneyBet;
            let ratio = 1;
            if(this.data.length>0 && this.last_close){
                ratio = this.last_close/this.data[this.data.length-1].Close;
            }
            moneyBet = moneyBet * ratio;
            moneyCash += moneyBet;
            this.player.asset = moneyCash ;
            this.player.pos = Math.max(this.min_pos,Math.min(this.max_pos,moneyBet/moneyCash))
            newdatum['asset']=moneyCash
        }

        this.sum_arr.push(this.last_close)
        if(!(this.sum_arr.length<this.movingavgdays)){
            this.sum_arr=this.sum_arr.slice(1);
        }
        newdatum['MA'] = Mathavg(this.sum_arr);
        this.data.push(newdatum)
    }

    digest_que(process_id, callback){//PID zero if its parent
        
        //depth+=`${Math.floor(Math.random()*10)}`;
        //console.log('pid'+process_id)
        //console.log('did'+depth)

        //No input que
        if(this.inputdata_que.length==0){
            console.log('chain_over')
            if(process_id==this.inputdata_PID){
                this.inputdata_PID = 0;
            }
            return 
        }

        // Is this an initial call?
        if(process_id==0){
            //digest_que is already in progress
            if(this.inputdata_PID){return}
            //initialize process id
            process_id = 1 + Math.floor(Math.random()*1000000)
            this.inputdata_PID = process_id;
        }
        else if(this.inputdata_PID!=process_id){return}
        
        const data = this.data.slice(this.plot_index);
        const height = this.height;
        const width = this.width;
        const margin = this.margin;
        const svg = this.svg;

        //shift animation

        // set and draw x axis
        this.xscale = d3.scaleLinear()
            .domain([data[0].dateind+1, data[data.length - 1].dateind+1])
            .range([margin.left, width - margin.right]);

        const shift = -(width - margin.right - margin.left)/data.length;

        svg.selectAll('g.xaxis')
        .transition()
        .duration(this.ANIM_INTERVAL)
        .ease(d3.easeElastic.period(this.ANIM_INTERVAL))
        .attr("transform", `translate(${shift},${height - margin.bottom})`)

        // draw asset line
        svg.select("path.asset")
            .datum(data)
            .transition()
            .duration(this.ANIM_INTERVAL)
            .ease(d3.easeElastic.period(this.ANIM_INTERVAL))
            .attr("transform", `translate(${shift},0)`)
        
        // draw moving average
        svg.select("path.MA")
            .datum(data)
            .transition()
            .duration(this.ANIM_INTERVAL)
            .ease(d3.easeElastic.period(this.ANIM_INTERVAL))
            .attr("transform", `translate(${shift},0)`)

        // draw moving average envelope
        svg.select("path.MAenv")
            .datum(data)
            .transition()
            .duration(this.ANIM_INTERVAL)
            .ease(d3.easeElastic.period(this.ANIM_INTERVAL))
            .attr("transform", `translate(${shift},0)`)

        this.candleobj
            .selectAll("g")
            .data(data)
            .transition()
            .duration(this.ANIM_INTERVAL)
            .ease(d3.easeElastic.period(this.ANIM_INTERVAL))
            .attr("transform", (d,i) => `translate(${this.xscale(d.dateind)},0)`)
            //fire another digest if needed
            // this firest for each element so its tricky to make it call only once at the end
            //.on( 'end' , ()=>{})
        
        setTimeout((() =>{
            //console.log('wai'+process_id)
            //console.log('did'+depth)
            if(this.inputdata_que.length>0){
                this.plot_index += 1;
                //console.log(this.inputdata_que)
                this.appendDatum(this.inputdata_que.shift());
                this.update();
                if(callback){
                    callback();
                    this.digest_que(process_id,callback);
                }
                else{
                    this.digest_que(process_id);
                }
            }
        }).bind(this),this.ANIM_INTERVAL)
    }

}

class d3posbar {
    constructor(svgid){
        this.svgid = svgid;
        this.svg = d3.select(`svg#${svgid}`);
        this.tbmargin=15;
        this.rr=2;
        this.ANIM_INTERVAL=300;

        this.data = [
            { 'name' : 'Cash' , 'value' : 1000. , 'color' : '#def' ,
             'x' : .43 , 'y' : null , 'width' : 0.1 , 'height' : 100} ,
            {'name' : 'Invested' , 'value' : 0 , 'color' : '#fea' ,
             'x' : .43 , 'y' : null , 'width' : 0.1 , 'height' : 100}];
        this.width = document.getElementById(svgid).clientWidth;
        
        let y1 = this.data[0].value;
        let y2 = this.data[0].value + this.data[1].value ;
        this.yscale = d3.scaleLinear()
        .domain([
            Math.min(-300, 100*Math.floor(1.*y1/100-1)),
            Math.max( 1300,300*Math.floor(1.1*y2/300+1))])
        .range([ document.getElementById(svgid).clientHeight - this.tbmargin, this.tbmargin ]);
        
        y1 = this.yscale(this.data[0].value);
        y2 = this.yscale(0);
        this.data[0].y = Math.min(y1,y2);
        this.data[0].height =Math.abs(y1-y2);

        y1 = this.yscale(this.data[0].value);
        y2 = this.yscale(this.data[0].value+this.data[1].value);
        this.data[1].y = Math.min(y1,y2);
        this.data[1].height = Math.abs(y1-y2);
    
        const portrects = this.svg.selectAll('g')
        .data(this.data)
        .enter();
        
        portrects.append('rect')
        .attr('class','pos')
        .attr('rx',this.rr)
        .attr('ry',this.rr)
        .attr('stroke-width', this.rr )
        .attr('fill',"rgba(0,0,0,0)")
        .attr('stroke',d => d.color )
        .attr('x',d => ( d.x - ((d.value<0) ? d.width+0.01 : 0) ) * this.width + this.rr/2)
        .attr('y',d => d.y + this.rr/2)
        .attr('width',d => Math.max(this.rr,d.width * this.width - this.rr))        
        .attr('height',d => Math.max(0,d.height - this.rr));      
        
        portrects.append('text')
        .attr('class','pos')
        .attr('text-anchor' , 'middle')
        .style('font-size', 12 )
        .style('font-family','Roboto')
        .style('stroke', 'white' )
        .text(d => d.name )
        .attr('x',d => ( d.x - ((d.value<0) ? (d.width+0.01)/2 : - d.width/2 ) ) * this.width)
        .attr('y', (d,i) => {
            if(i==0){ return d.y + d.height + this.rr + 10 }
            else{ return d.y - 2 * this.rr }
        });
        
        this.svg.append("g")
        .attr('class','yaxis')
        .attr("transform", `translate(${this.width*0.65},0)`)
        .attr('stroke', 'rgb(194,180,200)' )
        .style('font-size',12)
        .call(d3.axisRight(this.yscale)
            .tickFormat((num)=>{
                if(Math.abs(num)<1000){ return `${Math.floor(num)}` }
                return `${(num/1000).toFixed(1)}k`
            }))
        .call(g => g.select(".domain").style('opacity','0'))
        //.call(g => g.selectAll("text").attr('text-anchor' , 'end'))
        .call(g => g.selectAll("line")
            .attr('stroke-width', d => (d==0) ? this.rr*1.3 : this.rr/2 )
            .attr('stroke',  'rgba(194,180,200,0.5)')
            .attr('x1', -this.width*0.5 ));
    }
    
    update(val1,val2){
        if(val1 || val1===0){this.data[0].value=val1}
        if(val2 || val2===0){this.data[1].value=val2}
        
        this.width = document.getElementById(this.svgid).clientWidth;
        
        let y1 = this.data[0].value;
        let y2 = this.data[0].value + Math.max(0,this.data[1].value) ;
        this.yscale = d3.scaleLinear()
        .domain([
            Math.min(-300, 100*Math.floor(1.*y1/100-1)),
            Math.max( 1300,300*Math.floor(1.1*y2/300+1))])
        .range([ document.getElementById(this.svgid).clientHeight - this.tbmargin, this.tbmargin ]);
        
        y1 = this.yscale(this.data[0].value);
        y2 = this.yscale(0);
        this.data[0].y = Math.min(y1,y2);
        this.data[0].height =Math.abs(y1-y2);

        y1 = this.yscale(this.data[0].value);
        y2 = this.yscale(this.data[0].value+this.data[1].value);
        this.data[1].y = Math.min(y1,y2);
        this.data[1].height = Math.abs(y1-y2);
    
        const portrects = this.svg.selectAll('g.posblock')
        .data(this.data)
        
        this.svg.selectAll('rect.pos')
        .transition()
        .duration(this.ANIM_INTERVAL)
        .ease(d3.easeElastic.period(this.ANIM_INTERVAL))
        .attr('rx',this.rr)
        .attr('ry',this.rr)
        .attr('stroke-width', this.rr )
        .attr('fill',"rgba(0,0,0,0)")
        .attr('stroke',d => d.color )
        .attr('x',d => ( d.x - ((d.value<0) ? d.width+0.01 : 0) ) * this.width + this.rr/2)
        .attr('y',d => d.y + this.rr/2)
        .attr('width',d => Math.max(0,d.width * this.width - this.rr))        
        .attr('height',d => Math.max(0,d.height - this.rr));          
        
        this.svg.selectAll('text.pos')
        .transition()
        .duration(this.ANIM_INTERVAL)
        .ease(d3.easeElastic.period(this.ANIM_INTERVAL))
        .attr('text-anchor' , 'middle')
        .style('font-size', 12 )
        .style('font-family','Roboto')
        .style('stroke', 'white' )
        .text(d => d.name )
        .attr('x',d => ( d.x - ((d.value<0) ? (d.width+0.01)/2 : - d.width/2 ) ) * this.width)
        .attr('y', (d,i) => {
            if(i==0){ return d.y + d.height + this.rr + 10 }
            else{ return d.y - 2 * this.rr }
        });
        
        this.svg.selectAll("g.yaxis")
        .transition()
        .duration(this.ANIM_INTERVAL)
        .ease(d3.easeElastic.period(this.ANIM_INTERVAL))
        .attr("transform", `translate(${this.width*0.65},0)`)
        .attr('stroke', 'rgb(194,180,200)' )
        .style('font-size',12)
        .call(d3.axisRight(this.yscale)
            .tickFormat((num)=>{
                if(Math.abs(num)<1000){ return `${Math.floor(num)}` }
                return `${(num/1000).toFixed(1)}k`
            }))
        //.call(g => g.select(".domain").remove())
        //.call(g => g.selectAll("text").attr('text-anchor' , 'end'))
        .call(g => g.selectAll("line")
            .attr('stroke-width', d => (d==0) ? this.rr*1.3 : this.rr/2 )
            .attr('stroke',  'rgba(194,180,200,0.5)')
            .attr('x1', -this.width*0.5 ));
    }

}

class d3clock {
    constructor(svg){
        this.svg = svg;
        this.data = [ { 'name' : 'CASH' , 'value' : 10000. } ,
            {'name' : 'money-in' , 'value' : 0. }];
    
    }
}