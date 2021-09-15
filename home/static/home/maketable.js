function getTBdata(ticker_name){
    
  const close_set = window.localdb[`ticker__${ticker_name}`]["Close"];

  let pnt = close_set.length -1;
  let last_prices = [];
  while( pnt>=0 && last_prices.length<=25 ){
    let price = close_set[pnt]
    if(price){last_prices.push(price)};
    pnt=pnt-1;
  }

  let daily_str = "NA";
  let ma25_str = "NA";
  if(last_prices.length>1){daily_str = ((last_prices[0]-last_prices[1])/last_prices[1]*100)}
  if(last_prices.length>24){
    const ma25_price=Mathavg(last_prices.slice(0,25));
    ma25_str = ((last_prices[0]-ma25_price)/ma25_price*100)
  }

  return [daily_str,ma25_str];
};

// comment - This function depends on tickerboard so it might need to make it as an input when it's modulized.
function enterDailyFluct() {
  
  const daily_list = tickerboard.getElementsByClassName("daily");
  const ma25_list = tickerboard.getElementsByClassName("ma25");
  const len = daily_list.length;
  
  for(let i =0; i<len; i++){
    
    const dailyDOM = daily_list[i];
    const ma25DOM = ma25_list[i];
    //Assuming here dailyDOM.id==ma25DOM.id
    if(window.localdb["ticker__" +dailyDOM.id]){

      let [da,ma] =  getTBdata(dailyDOM.id);
      
      if(da=="NA"){
        dailyDOM.style.color="white";
        dailyDOM.innerHTML=da;
      }
      else if((da.toFixed(2) + '%')!=dailyDOM.innerHTML){
        dailyDOM.style.color="white";
        dailyDOM.innerHTML = (da.toFixed(2) + '%');
        setTimeout(()=>{
          dailyDOM.style.color=(da<0) ? "LightCoral" : "lightgreen";
        },300)
      };

      if(ma=="NA"){
        ma25DOM.style.color="white";
        ma25DOM.innerHTML=ma;
      }
      else if((ma.toFixed(2) + '%')!=ma25DOM.innerHTML){
        ma25DOM.style.color="white";
        ma25DOM.innerHTML = (ma.toFixed(2) + '%');
        setTimeout(()=>{
          ma25DOM.style.color=(ma<0) ? "LightCoral" : "lightgreen";
        },300)
      }

    }
    
  };
};

function getMonthByInd(ind){
  return (new Date(1900,0,ind)).getMonth();
};

function makeTableData(tag){

  let data=[];

  Object.keys(window.localdb).forEach((el)=>{
    let key=el.split("__");
    if(key[0]!=tag){return;};

    let strt_date=window.localdb[el].strt_date;
    let end_date=window.localdb[el].end_date;

    let thismonth = getMonthByInd(end_date-1);
    let asset_thismonth = window.localdb[el].asset[end_date-1-strt_date];
    let lastmonth = end_date-1;
    while(lastmonth>strt_date && getMonth(lastmonth)==thismonth){lastmonth-=1};
    let asset_lastmonth = window.localdb[el].asset[lastmonth-strt_date];
    let monthly_gain=(asset_thismonth/asset_lastmonth-1)*100;

    data.push([ key[1], monthly_gain, asset_thismonth ]);
  });

  return data;
}


function enterTableData(tableId, data, sortind){

  let tableElement = document.querySelector('table#'+tableId);
  let tableMeta = document.querySelector(`meta[name='meta#${tableId}']`);
  if(!tableMeta){
    tableMeta = document.createElement(`meta`);
    tableMeta.name = "meta#"+tableId;
    tableMeta.content = "0:▼:▲";
    tableElement.appendChild(tableMeta);
  }

  let thElements = tableElement.getElementsByTagName('thead')[0].getElementsByTagName('th');
  let sortInfo = tableMeta.content.split(":");
  //Remove an arrow to thead
  sortInfo[0]=parseInt(sortInfo[0]);
  if(sortInfo[0]!=0){
    thElements[Math.abs(sortInfo[0])].innerText=thElements[Math.abs(sortInfo[0])].innerText.slice(0,-1);
  }
  //Add an arrow to thead
  let reverseflag = (sortInfo[0]!=-sortind);
  if(sortind!=0){
    thElements[sortind].innerText += ( reverseflag ? sortInfo[2] : sortInfo[1] );
  }
  sortInfo[0]= ( reverseflag ? -sortind : sortind )
  tableMeta.content = sortInfo.join(":")

  //Sorting
  sortdata(data,sortind-1,reverseflag)

  //Recontruct tbody
  const tbodyEl=tableElement.getElementsByTagName('tbody')[0];
  tbodyEl.innerHTML="";
  let rownum=0;
  data.forEach((el)=>{
    let row = tbodyEl.insertRow(rownum);
    rownum++;
    row.innerHTML = `<td><a href='/portfolio/ranking/help/'>${getBadge(el[2],true)}</a></td>`;
    //row.innerHTML += `<td><a href="portfolio/overview/${el[0]}/">${el[0]}</a></td>`;
    row.innerHTML += `<td><a href="portfolio/overview/${el[0]}/">${ (el[0].length>7) ? el[0].slice(0,7)+'...' : el[0] }</a></td>`;
    row.innerHTML += `<td>${numformat(el[1])}%</td>`;
    row.innerHTML += `<td>${numformat(el[2])}</td>`;
  });
}

function block0height(){
  return (window.innerHeight/2-315)+"px";
}

function resize(){
  window.plotly.layout.width = document.getElementById("content-main1").clientWidth/2;
  window.plotly.layout.height = document.getElementById("content-main1").clientWidth/2 ;
  maincontent0.style.height=block0height();
  window.plotly.layout.yaxis2.autorange=true;
  if(window.innerWidth>document.getElementById("content-main1").clientWidth){
    document.getElementById("content").style="justify-content: center;"
  }
  else{
    document.getElementById("content").style="justify-content: flex-start;"
  }
  window.plotly.plot();
  //let gtb = document.querySelector('g.trace.boxes')
  //if(gtb){
  //  gtb.querySelectorAll('path.box').forEach(el => {
  //    el.style.setProperty('stroke-width','1px');
  //    el.style.setProperty('fill-opacity','1');
  //})}
}


//////////////////////////////////
//window.plotly variables onload//
//////////////////////////////////
// comment - The following block is running on homepage.html if you add script in homepage.html (I remove for the next commit)
// The setIntervals fetching overlapped information in homepage.html. Functions are defined twice in hompage.html if you include this file.
// DISPLAY_DATES = 3 will not work for ma25 and also for holidays. It also makes ambiguous on what value it is in hompage.html.
DISPLAY_DATES = 3;
setInterval(()=>{
  if(document.hasFocus()){
    let request={};
    const daily_list = tickerboard.getElementsByClassName("daily");
    for(let i = 0 ; i < daily_list.length; i++ ){
      const ticker_key = 'ticker__'+daily_list[i].id;
      request[ticker_key]=window.localdb_meta.__todayind-DISPLAY_DATES;
    }
    Object.keys(window.localdb).forEach((key)=>{
      if(key in request){
        request[key]=Math.min(request[key],window.localdb[key].end_date-1);
      }
      else if(key.split("__")[0]=="player" || key=='ticker__'+window.drawnTicker){
        request[key]=window.localdb[key].end_date-1;
      }
    });

    fetchDB(request).then((response_json)=>{
      // window.rbdata = makeTableData("player");
      // enterTableData("rankingboard", window.rbdata , 0 );
      // enterTableData("rankingboard", window.rbdata , 2 );
      enterDailyFluct();
      console.log("fetch complete")
      // Object.keys(window.localdb).forEach((key)=>{
      //   if(key.split("__")[0]=="player" || key=='ticker__'+window.drawnTicker){
      //     window.plotly.enter(key,DISPLAY_DATES)
      //   }
      // });
      // window.plotly.plot();
      saveLocalDB();
    })
  }
},10000)