
function apply(obj,argv){
    let newobj=obj;
    argv.forEach((arg)=>{
        switch(arg[0]) {
            case 'data': newobj=newobj.attr(arg[1],arg[2]); break
            case 'attr': newobj=newobj.attr(arg[1],arg[2]); break;
            case 'style': newobj=newobj.style(arg[1],arg[2]); break;
            case 'text': newobj=newobj.text(arg[1]); break;
            case 'on': newobj=newobj.on(arg[1],arg[2]); break;
            case 'transition': newobj=newobj.transition(); break;
            case 'ease': newobj=newobj.ease(arg[1]); break;
            case 'delay': newobj=newobj.delay(arg[1]); break;
            case 'duration': newobj=newobj.duration(arg[1]); break;
            case 'append': newobj=newobj.append(arg[1]); break;
            case 'call': newobj=newobj.call(arg[1]); break;
        }
    })
    return newobj;
}


function getD3(obj,tag){
    return obj.svg.selectAll(tag).data(obj.pointlist)
}

function moneyForm (quant){
    if(parseInt(quant)==quant){
        return `${quant}`
    };
    if(quant<1000){
        return quant.toFixed(2)
    };
    quant/=1000;
    if(quant<1000){
        return quant.toFixed(2)+"k"
    }
    return (quant/1000).toFixed(2)+"M";
}

class d3chart {
    constructor(svg,numRows,qname){

        this.qname=qname
        if(!qname){
            this.qname="svg";
        }

        this.svg=svg;

        this.pointlist = [];
        this.datelist = [];

        this.yShift=100;
        this.yOffSet=30;//50;
        this.xOffSet=window.innerWidth/2.;
        this.rectHeight=50;
        this.rectWidth=1./200/1000;

        this.textlist=['ticker','quant','amt'];
        this.textOffSet={'ticker':27,'quant':40 , 'amt':65, 'date':24,'asset':39};
        this.fontSize={'ticker':'17px','quant':'10px','amt':'10px','date':'13px','asset':'13px'};
        this.textSVG={'ticker':{},'quant':{} , 'amt':{}};
        
        this.lrmargin=1.9;
        this.datemargin=20;
        this.tickertextyoffset=25;

        this.assetlist = [];
        this.monthMap = {}//index to date
        this.numRows = numRows;
        this.animationPlaying=0; // object becomes draggable when animation done
        this.nump=0; // number of Points

        this.maxSVGwidth=1000.;
        this.svgwidth=1000.;

        this.hoverticker="";

        //this.categoryScale = d3.scaleOrdinal(d3.schemeTableau10);
        //"#4e79a7" 573857 "Cash(USD)"
        //"#e15759" 1062262 MRNA
        //"#f28e2c" 592013 COST
        //this.colorList = ['#76b7b2',"#59a14f","#e15759","#f28e2c","#af7aa1","#ff9da7","#9c755f","#4e79a7","#bab0ab","#edc949"];
        this.colorList = [
            '#76b7b2',"#59a14f","#e15759","#f28e2c","#456bc3",
            "#ab613c","#c2b384","#4e79a7","#bab0ab","#e8b143",
        ];
        this.colors = {};

        this.empty_point={'x':0,'y':0,'width':2*this.lrmargin,'height':0,rawx:0,rawy:0,rawwidth:2*this.lrmargin/this.svgwidth,ticker:"_cash"};

        this.svg.attr('height',this.yOffSet);

        this.pos_update = [
            ['attr' , 'x' , (d) => {return d.x;}],
            ['attr' , 'y', (d) => {return d.y;}],
        ]

        this.rect_init=[
            ['attr' , 'class' , 'draggable'],
            ['attr' , 'rx' , 6 ],
            ['attr' , 'ry' , 6 ],
            ['attr' , 'stroke-width', 3 ],
            ['attr' , 'fill' , 'rgba(0,0,0,0)'],
            ['style' , 'opacity' , 0],
            ['attr' , 'transform' , `translate(${this.lrmargin},0)`],
            ['attr' , 'x' , (d) => {return d.x;}],
        ]

        this.rect_visset=[
            ['attr' , 'width', d => Math.max(d.width-2*this.lrmargin,0)],
            ['attr' , 'height', d => d.height],
            ['attr' , 'stroke', d => this.colors[d.ticker]]
        ]

        this.text_init = (field)=>[
            ['attr' , 'class' , field+'text'],
            ['attr' , 'text-anchor' , 'middle'],
            ['style' , 'font-size' , this.fontSize[field]],
            ['attr' , 'y', this.yOffSet],
            ['text' , (d) => { return d[field]; }],
            ['attr' , 'x' , (d,i) => {
                if(d.textopactiy!=false){
                    let textwidth=document.getElementsByClassName(field+'text')[i].getComputedTextLength()
                    d['textopactiy']=(textwidth<d.width-2*this.lrmargin) ? 1 : 0;    
                }
                return d.x;
            }],
            ['style' , 'opacity' , 0],
        ]

        this.text_visset = (field)=>[
            ['attr' , 'fill', (d) => {return this.colors[d.ticker]}],
            ['text' , (d) => { return d[field]; }],
            ['attr' , "transform" , (d) => {
                let y=this.textOffSet[field]
                if(field!="amt"){
                    y-= (d.textopactiy) ? 0 : this.yShift*0.45
                }
                return `translate(${d.width/2},${y})`
            }],
        ]

        this.text_opacity = (field)=>[
            ['style' , 'opacity' ,  (d) => {return (d.ticker!="Cash(USD)" || field!="amt") ? d.textopactiy : 0}],
        ]

        this.init_transition = (monthindex) => [
            [ 'transition' ],
            [ 'delay' , 100*monthindex ],
            [ 'ease' , d3.easeExp ],
            [ 'duration' , 400 ]
        ]

        this.slide_transition = [
            [ 'transition' ],
            [ 'ease' , d3.easeExp ],
            [ 'duration' , 600 ]
        ]
    }
    
    //colorScale(d) {return d === 0 ? '#777' : d3.scaleOrdinal(d3.schemeTableau10)(d);}

    addRectRow(history){

        this.svg.attr('height',document.querySelector(this.qname).clientHeight+this.yShift);

        let acc=0.;
        let monthindex=Object.keys(this.monthMap).length;
        this.monthMap[history.date]=monthindex
        this.datelist.push({date:history.date,asset:moneyForm(history.asset)});
        this.svgwidth=Math.min(this.maxSVGwidth,document.querySelector(this.qname).clientWidth);
        this.datelist[monthindex].y = (this.numRows-1-monthindex)*this.yShift+this.yOffSet;
      
        Object.keys(history.portfolio_money).forEach((ticker)=>{
            
            this.animationPlaying++;
            let amount=history.portfolio_money[ticker];
            let quant=history.portfolio_quant[ticker];

            ticker=(ticker=="_cash") ? "Cash(USD)" : ticker;
            if(this.colors[ticker]==undefined){
                //this.colors[ticker]=this.categoryScale(parseInt(ticker,36))
                let tickerint=parseInt(ticker.replaceAll('^','0'),36);
                if(tickerint==Infinity){
                    tickerint=14125623;
                }
                let color = this.colorList[tickerint%this.colorList.length];

                let r = parseInt(color.slice(1,3),16);
                let g = parseInt(color.slice(3,5),16);
                let b = parseInt(color.slice(5,7),16);

                r += (tickerint **2 % 60 -15)
                g += (tickerint **3 % 60 -15)
                b += (tickerint **4 % 60 -15)

                if(r>255){r=511-r}
                if(g>255){r=511-g}
                if(b>255){r=511-b}

                this.colors[ticker]='#'+r.toString(16)+g.toString(16)+b.toString(16)                
            };

            this.pointlist.push({
                'acc' : acc,
                'monthindex' : monthindex,
                'amount' : amount,
                'rawx' : (acc - history.asset/2)*this.rectWidth,
                'rawwidth' : (amount*this.rectWidth),
                'x' : (acc - history.asset/2)*this.rectWidth*this.svgwidth +0.5*document.querySelector(this.qname).clientWidth,
                'y' : (this.numRows-1-monthindex)*this.yShift+this.yOffSet,
                'width' : (amount*this.rectWidth)*this.svgwidth,
                'height' : this.rectHeight,
                'ticker' : ticker,
                'quant' : moneyForm(quant),
                'amt' : moneyForm(amount)
            })
            this.assetlist.push(history.asset);
            acc+=amount;
        });
        
        
    
    
        let row=getD3(this,'g.row')
            .enter()
            .append('g')
            .attr('class','row')
        
        Array('ticker','quant','amt').forEach((field)=>{
            this.textSVG[field]=apply(
                row.append('text')
                ,this.text_init(field))
        })

        apply(apply(apply(
            row.append('rect')
            ,this.rect_init)
            ,this.rect_visset)
            .attr("y", this.yOffSet)
            ,this.init_transition(monthindex))
            .attr("y", (d)=>{return d.y;})
            .style("opacity",1)
            .on('end',()=>{
                this.animationPlaying--;
             })
        
        Array('ticker','quant','amt').forEach((field)=>{
            apply(apply(apply(
                this.textSVG[field]
                ,this.text_visset(field))
                ,this.init_transition(monthindex))
                .attr("y", (d)=> d.y)
                ,this.text_opacity(field))        
        });

        let sidebar=this.svg.selectAll('g.side')
            .data(this.datelist)
            .enter()
            .append('g')
            .attr('class','side')

        Array('date','asset').forEach((field)=>{
            apply(
                sidebar
                .append('text')
                .attr('class',field+'text')
                .attr('text-anchor' , 'end')
                .text(d=>d[field])
                .attr('fill', 'rgba(255,255,255,0.8)')
                .attr('x', document.querySelector(this.qname).clientWidth-this.datemargin)
                .attr('y', this.yOffSet )
                .style('font-size',this.fontSize[field])
                .style('opacity',0)
                ,this.init_transition(monthindex))
                .attr('y', d => d.y + this.textOffSet[field] )
                .style('opacity',1)
        })
    };
}

let chrt={};

function handleMouseOver(d,i){
    chrt.hoverticker=chrt.pointlist[i].ticker;
    getD3(chrt,"rect")
        .style('opacity', (d) => {
            return (d.ticker!=chrt.hoverticker) ? 0.5 : 1;
        })
    getD3(chrt,'text.tickertext')
        .style('opacity', (d) => {
            return (d.ticker!=chrt.hoverticker) ? 0.5*d.textopactiy : 1;
        })
    getD3(chrt,'text.quanttext')
        .style('opacity', (d) => {
            return (d.ticker!=chrt.hoverticker) ? 0.5*d.textopactiy : 1;
        })
    getD3(chrt,'text.amttext')
        .style('opacity', (d) => {
            if(d.ticker=="Cash(USD)"){ return 0 };
            return (d.ticker!=chrt.hoverticker) ? 0 : 1;
        })
};


function handleMouseOut(d,i){
    chrt.hoverticker="";
    getD3(chrt,"rect")
        .style('opacity',1)
    getD3(chrt,'text.tickertext')
        .style('opacity',d => d.textopactiy)
    getD3(chrt,'text.quanttext')
        .style('opacity',d => d.textopactiy)
    getD3(chrt,'text.amttext')
        .style('opacity',0)
}

function dragstarted(d,i) {
    chrt.pointlist[chrt.nump]=chrt.pointlist[i];
    apply(apply(
        getD3(chrt,'rect')
        ,chrt.rect_visset)
        ,chrt.pos_update)
}

function dragged(d,i) {
    d.x=d3.event.x;
    Array('rect','text.tickertext','text.quanttext','text.amttext').forEach((field)=>{
        apply(getD3(chrt,field),chrt.pos_update)
    })
}

function dragended(d,i) {

    let flag=-1;

    if(i>0 && chrt.pointlist[i].monthindex==chrt.pointlist[i-1].monthindex && chrt.pointlist[i-1].x+chrt.pointlist[i-1].width/2>d.x){
        flag=0;
    }
    if(i < chrt.nump-1 && chrt.pointlist[i].monthindex==chrt.pointlist[i+1].monthindex && chrt.pointlist[i+1].x+chrt.pointlist[i+1].width/2<d.x+d.width){
        flag=1;
    }
    if(flag>=0){
        let ptrL=chrt.pointlist[i+flag-1];
        let ptrR=chrt.pointlist[i+flag];
        
        ptrR.acc=ptrL.acc;
        ptrL.acc=ptrR.acc+ptrR.amount;

        ptrR.rawx=(ptrR.acc - chrt.assetlist[i+flag]/2)*chrt.rectWidth;
        ptrL.rawx=(ptrL.acc - chrt.assetlist[i-1+flag]/2)*chrt.rectWidth;

        chrt.pointlist[i+flag]=ptrL;
        chrt.pointlist[i-1+flag]=ptrR;
    }

    apply(apply(
        getD3(chrt,'rect')
        ,chrt.rect_visset)
        ,chrt.pos_update)
    
    Array('ticker','quant','amt').forEach((field)=>{
        apply(apply(apply(
            getD3(chrt,`text.${field}text`)
            ,chrt.text_visset(field))
            .style('opacity',d=>d.textopactiy)
            ,chrt.pos_update)
            ,chrt.slide_transition)
            .attr('x', (d) => {
                let newx=d.rawx*chrt.svgwidth+0.5*document.querySelector(chrt.qname).clientWidth;
                if(field=='amt'){d.x=newx};
                return newx;
            })
    })
    
    apply(
        getD3(chrt,"rect")
        .call(dragOff)
        ,chrt.slide_transition)
        .attr('class', 'draggable')
        .attr( 'x', d => d.x )
        .on('end',()=>{
            chrt.pointlist[chrt.nump]=chrt.empty_point;
            update()
            .attr('class',(d,i)=>{
                return (i==chrt.nump) ? 'dragging' : 'draggable' ;
            })
            chrt.svg.selectAll("rect")
            .call(dragOn)
        })
}

let dragOn=d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended);

let dragOff = d3.drag()
    .on("start", null)
    .on("drag", null)
    .on("end", null);

function update(){
    return apply(apply(
        getD3(chrt,'rect')
        ,chrt.rect_visset)
        ,chrt.pos_update)
}

function updateText(){
    apply(getD3(chrt,"text.tickertext"),chrt.text_visset('ticker'))
    apply(getD3(chrt,"text.quanttext"),chrt.text_visset('quant'))
}

function draginit() {
    chrt.nump = chrt.pointlist.length;
    chrt.pointlist.push(chrt.empty_point);
    
    apply(getD3(chrt,'rect')
        .enter()
        .append('rect')
        ,chrt.rect_init)
        .attr('class', 'dragging')
}

function resizeChrt(){
    chrt.svgwidth = Math.min(chrt.maxSVGwidth,document.querySelector(chrt.qname).clientWidth);
    getD3(chrt,"rect")
    .attr('x', (d) => {d.x=(d.rawx*chrt.svgwidth+0.5*document.querySelector(chrt.qname).clientWidth);return d.x;})
    .attr('width', (d) => {d.width=(d.rawwidth*chrt.svgwidth);return Math.max(d.width-2*chrt.lrmargin,0)});
    chrt.pointlist.forEach((d)=>{
        d.textopactiy=true;
    });
    Array('ticker','quant','amt').forEach((field)=>{
        apply(getD3(chrt,`text.${field}text`),[chrt.text_init(field)[5]])
    });
    Array('ticker','quant','amt').forEach((field)=>{
        apply(getD3(chrt,`text.${field}text`),[chrt.text_visset(field)[2]])
    });
    handleMouseOut(null,null);
    chrt.svg.selectAll('text.datetext,text.assettext')
    .attr('x', document.querySelector(chrt.qname).clientWidth-chrt.datemargin);
}