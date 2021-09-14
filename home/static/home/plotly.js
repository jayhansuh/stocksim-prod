window.plotly={};

window.plotly['data']=[];

window.plotly['dataInd']={};

window.plotly['config']= {'scrollZoom': true };

window.plotly['layout'] = {
    autosize: false,
    dragmode: "pan",
    showlegend: false,
    
    xaxis: {
        autorange: true,
        gridcolor: "rgba(255,165,0,0.2)",
        rangeslider: {
            visible: false,
        },
        // rangeselector: {
        //     buttons: [
        //         {
        //         count: 3,
        //         label: "3 mo",
        //         step: "month",
        //         stepmode: "backward",
        //         },
        //         {
        //         count: 6,
        //         label: "6 mo",
        //         step: "month",
        //         stepmode: "backward",
        //         },
        //         {
        //         count: 1,
        //         label: "1 yr",
        //         step: "year",
        //         stepmode: "backward",
        //         },
        //         {
        //         count: 1,
        //         label: "YTD",
        //         step: "year",
        //         stepmode: "todate",
        //         },
        //         { step: "all" },
        //     ],
        // },
        title: "",
    },

    yaxis: {
        type: "log",
        autorange: true,
        fixedrange: false,
        gridcolor: "rgba(155,165,200,.2)",
        tickfont: { color: "rgba(68,156,192,1.)" },//"rgba(47,156,190,1.)"
    },

    yaxis2: {
        type: "log",
        autorange: true,
        tickfont: { color: "rgba(204,132,0,1.)"},//"rgba(255,165,0,1.)" },
        scaleanchor: "y",
        overlaying: "y",
        side: "right",
        position: 1,
        gridcolor: "rgba(255,165,0,0.1)",

    },

    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 35, r: 35, t: 40, b: 30 },

};

window.plotly['plot'] = () => {
    return Plotly.newPlot('chartplot', window.plotly.data,  window.plotly.layout ,  window.plotly.config);
}

window.plotly['datastyle']={
    
    'player':JSON.stringify({
        type: "scatter",
        mode: "lines",
        name: null,
        x: null,
        y: null,
        line: {color: '#17BECF'},
    }),

    'ticker':JSON.stringify({
        x: null,
        close: null,
        high: null,
        low: null,
        open: null,

        // cutomise colors
        increasing: {line: {color: 'lightblue',width:1}},
        decreasing: {line: {color: 'pink'}},
        //increasing: {line: {color: 'rgb(173 224 169)'}},
        //decreasing: {line: {color: 'rgb(220 83 83)'}},

        line: {'stroke-width': "1px"},
        
        type: 'candlestick',
        xaxis: 'x',
        yaxis: 'y2',
        //'fill-opacity':'1',
        //'stroke-width':'1px',

        text : "12",
        hoverinfo : 'x+y',

        hoverlabel:{
          bgcolor:"white",
          bordercolor:"gray",
          font_size:14,
          font_family:"Roboto",
        },
    }),
}

window.plotly['enter']=(key,max_len=Infinity)=>{
    const locald=window.localdb[key];
    if(!locald){return;}
    const k = key.split("__");
    const datum = JSON.parse(window.plotly.datastyle[k[0]]);
    const x = dateslice(locald.strt_date,locald.end_date-locald.strt_date);
    let sliceind=Math.max(0,locald.end_date-locald.strt_date-max_len);

    if(k[0]=="player"){
        datum.name=k[1];
        datum.x=x.slice(sliceind);
        datum.y=locald.asset.slice(sliceind);
    }
    else if(k[0]=="ticker"){
        datum.x=x.slice(sliceind);
        datum.close = locald.Close.slice(sliceind)
        datum.high = locald.High.slice(sliceind)
        datum.low = locald.Low.slice(sliceind)
        datum.open = locald.Open.slice(sliceind)
    }

    if(key in window.plotly.dataInd){
        window.plotly.data[window.plotly.dataInd[key]]=datum;
    }
    else{
        window.plotly.dataInd[key]=window.plotly.data.length;
        window.plotly.data.push(datum)
    }

}

window.plotly['drop']=(key)=>{

    if(!(key in window.plotly.dataInd)){ return };

    let delInd=window.plotly.dataInd[key];
    
    delete window.plotly.dataInd[key];
    window.plotly.data.splice(delInd,1);
    
    Object.keys(window.plotly.dataInd).forEach((key)=>{
        if(window.plotly.dataInd[key]>delInd){
            window.plotly.dataInd[key]-=1;
        }
    })

}