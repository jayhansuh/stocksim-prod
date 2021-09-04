function numformat(num){
  let unit=" "
  if(num>=1000){
    num/=1000;
    if(num>=1000){
      num/=1000;
      unit="M"
    }
    else{
      unit="k"
    }
  }
  let precision=Math.min(2,2-Math.floor(Math.log10(Math.abs(num))));
  return (num<0 ? "" : " ")+num.toFixed(precision)+unit
}

function sortdata(data,sortind,reverseflag=false){
  data.sort((el1,el2)=>{
    let val1 = el1[sortind]; // ignore upper and lowercase
    let val2 = el2[sortind]; // ignore upper and lowercase
    if(typeof(val1)=='string'){val1=val1.toUpperCase()}
    if(typeof(val2)=='string'){val2=val2.toUpperCase()}
    if (val1 < val2) { return -1; }
    if (val1 > val2) { return 1; }
    return 0;
  });
  if(reverseflag){data.reverse()};
}

function sortkeyformat(num){
  // "pDD0000000"
  // p,m : sign
  // DD : log10 digits
  // 000000 : floating number
  // negative value gives the overflow format
  if(num==0){
    return "o";
  }

  let sortkey="";

  // sign part
  let sign = (num>0) ;
  sortkey += (sign) ? "p" : "n";
  let abs = Math.abs(num);

  // DD part
  const MAXDD=99;
  let DD=Math.floor(Math.max(0,Math.log10(abs)));
  if(DD>MAXDD){
    console.log("Too extreme number for the function sortkeyformat")
    return (sign == "p") ? "q" : "l"; // q, l : +, - infinity
  }
  abs=abs/(10**(DD+1));
  if( !sign ){ DD = MAXDD - DD };
  sortkey += ((DD<10) ? "0" : "") + DD;

  // float part
  const MAXFLOATS=4;
  if( !sign ){ abs = 1 - abs };
  abs = abs.toFixed(MAXFLOATS);
  if(abs.slice(0,2)=="1."){
    sortkey += "a";
  }
  else{
    sortkey += abs.slice(2);
  }

  return sortkey
}

function Mathavg(arr){
  let ans = 0. ;
  arr.forEach(el => (ans+=el) );
  return ans/arr.length;
}

function transpose(array){
  return array[0].map((_, colIndex) => array.map(row => row[colIndex]));
}

function randSelect(obj){
  if(typeof(obj)!='object'){throw 'randSelect must get an object'}
  const arr = Array.isArray(obj) ? obj : Object.keys(obj);
  return arr[Math.floor(Math.random()*arr.length)];
}

function applyStyle(DOM,style_obj){
  Object.keys(style_obj).forEach( key => {
		DOM.style.setProperty( key , style_obj[key] );
	})
}

function appendGuideLayer(dom){
  const guidelayer = document.createElement('svg');
	const style_obj = {
		width: '100vw',
    height: '100vh',
    position: 'absolute',
    top: 0,
    left: 0,
    background: '#555',
    opacity: 0.4,
    'z-index': 9,
    'transition': 'opacity 0.2s',
  };
  applyStyle(guidelayer,style_obj)
	guidelayer.onclick = () => console.log('guidlayer onclick');
  dom.appendChild(guidelayer);
  return guidelayer;
}

function appendTextBox(dom){

  const textbox = document.createElement('div');
  textbox.className="glowdim";
  applyStyle(textbox,{
    'position':'absolute',
    'align-items': 'center',
    'justify-content': 'center',
    'display': 'flex',
    'z-index': 10,
    'text-shadow': '0 0 5.4px #555, 0px 0px 1.5px #555, 0px 0px 0.6px #555, 0px 0 36px #555, 0px 0 12px #888',
  });
  dom.appendChild(textbox);

  // const text = document.createElement('div');
  // applyStyle(text,{
  //   'text-align':'center',
  //   'color': 'white',
  //   'text-shadow': '0 0 5.4px #555, 0px 0px 1.5px #555, 0px 0px 0.6px #555, 0px 0 36px #555, 0px 0 12px #888',
  // })
  // textbox.appendChild(text);

  return textbox;
}