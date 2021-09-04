function npolyGen(n,yi,yf,shadow){

    if(!yi){yi=20}
    if(!yf){yf=100}
    if(!shadow){shadow=0}
    const color='#d2ebf9';

    if( n > 12 ){
        return `<circle style="fill: black;stroke:none;filter:drop-shadow(0px 0px ${shadow}px rgb(255 255 255 / .9));" cx="50" cy="${((yi+yf)/2).toFixed(3)}" r="${((yf-yi)/2).toFixed(3)}"></circle>`;
    }

    const nang = 2 * Math.PI / n;
    const offang = (n%2 == 0) ? nang / 2 : 0;

    //const radius = 50;
    //const yoffset = 100. / ( Math.cos(offang) + Math.cos(nang/2) );
    const radius = (yf-yi) / ( Math.cos(offang) + Math.cos(nang/2) );
    const yoffset = yf - radius * Math.cos(nang/2) ;

    const points = [];
    for(let i = 0 ; i < n ; i++ ){
        points.push([
            50 + radius * Math.sin( offang + i * nang ),
            yoffset - radius * Math.cos( offang + i * nang ),
        ])
    }
    let dstr="M";
    points.forEach(el => {
        dstr += ` ${el[0].toFixed(3)} ${el[1].toFixed(3)} L`
    })
    dstr=dstr.slice(0,dstr.length-1)+'Z';
    //return `<path d="${dstr}" style="fill: rgb(216, 216, 216);stroke:none;"></path>`
    
    return `<path class="badge" d="${dstr}" style="fill: ${color};stroke:none;filter:drop-shadow(0px 0px ${shadow}px rgb(255 255 255 / 0.7));"></path>`

    //black hole
    //return `<path class="badge" d="${dstr}" style="fill: black;stroke:none;filter:drop-shadow(0px 0px ${shadow}px rgb(255 255 255 / 0.7));"></path>`
}

function getBadge(asset,shadowOn){
    let n = 3;
    if(asset>1000000){n = 13;}
    else{
        n += Math.floor(Math.max( 0 , 3 * Math.log2(asset/(100000))))
    }
    //style="width:13px"
    return `<svg  height='21' style='margin:-5px -5px -5px -1px;' viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">${(shadowOn) ? npolyGen(n,25,75,11) : npolyGen(n,20,100,0)}</svg>`;
    
    // const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    // svg.setAttribute('style','height:100%;');
    // svg.setAttributeNS("http://www.w3.org/2000/svg", "viewBox", "0 0 100 100");
    // svg.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    // svg.innerHTML= (shadowOn) ? npolyGen(n,25,75,13) : npolyGen(n,20,100,0);
    // return svg
}