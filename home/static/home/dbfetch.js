//Initializing window.localdb
window.localdb_meta = JSON.parse(window.localStorage.getItem("localdb_meta"));
if (!window.localdb_meta) {
    window.localdb_meta = {__keys:[]};
}
window.localdb={};
window.localdb_meta.__keys.forEach((key)=>{
    window.localdb[key]=JSON.parse(window.localStorage.getItem(key))
})

window.localdb_meta['__todayind']=Math.floor((Date.now()-(new Date(1900,0,1)).getTime())/(24*60*60*1000))+1;

function saveLocalDB(){
    if(window.localdb_meta.__keys.length===0){
        console.log("Nothing in the save queue")
        return;
    }
    try{
        window.localdb_meta.__keys.forEach((key)=>{
            if(window.localdb_meta[key].saved===false){
                window.localStorage.setItem(key, JSON.stringify(window.localdb[key]));
                window.localdb_meta[key].saved=true;
            }
        })
        window.localStorage.setItem("localdb_meta",JSON.stringify(window.localdb_meta))
    }
    catch(err){
        console.error(err);
        const lastkey = window.localdb_meta.__keys.pop();
        if(lastkey in window.localdb_meta){
            delete window.localdb_meta[lastkey]
        }
        if(key in window.localStorage){
            window.localStorage.removeItem(key);
        }
        saveLocalDB()
    }
}

function clearLocalDB(){
    window.localdb={};
    window.localdb_meta = {__keys:[]};
    window.localStorage.clear();
}

function updateData(newdata,target){
    let prepend_arr=[];
    while(newdata.strt_date<target.strt_date){
        prepend_arr.push(null);
        target.strt_date-=1;
    }
    let splice_strt=newdata.strt_date-target.strt_date;

    let len=Infinity;
    Object.keys(newdata).forEach((key)=>{if(key!='strt_date'){
        if(!(key in target)){target[key]=[]};
        target[key].splice(0,0,...prepend_arr)
        target[key].splice(splice_strt,newdata[key].length,...newdata[key])
        len=Math.min(len,target[key].length);
    }});
    
    len = (len==Infinity) ? 0 : len;
    target['end_date']=target.strt_date+len;
}

//__date rule 1900 Jan 01 -> 1 , 1900 Feb 01 -> 32 , ... 2022 May 20 -> 44700
function updateDB(data_json){
    if('error' in data_json){throw data_json.error;};
        
    if('clearProtocol' in data_json){clearLocalDB();delete data_json['clearProtocol'];};
    
    Object.keys(data_json).forEach((key)=>{
        if(!(key in window.localdb)){
            window.localdb[key]={strt_date:data_json[key].strt_date}
            window.localdb_meta[key]={};
        };
        updateData(data_json[key],window.localdb[key])
        window.localdb_meta[key]['saved']=false;
        let ind=window.localdb_meta.__keys.indexOf(key)
        if(ind>=0){window.localdb_meta.__keys.splice(ind,1)}
        window.localdb_meta.__keys.unshift(key)
    });
}

async function fetchDB(req){
    try{
        const response = await fetch('/stockdb/_get_meta?req='+((typeof(req)=="string") ? req : JSON.stringify(req)));
        const response_json = await response.json(); // parses JSON response into native JavaScript objects
        updateDB(response_json)
        return response_json;
    }
    catch(err){
        console.error(err)
        return null;
    }
}

function indtodate(ind){
    return (new Date(1900,0,ind)).toISOString().slice(0,10)
}

function dateslice(strt_date,len){

    //initialize datelist if it's undefined or null
    if(!window.datelist){
        window.datelist={strt_date:strt_date,data:[]};
    }

    //prepend if strt_date is out of index
    let prepend_flag=false;
    if(window.datelist.strt_date>strt_date){
        prepend_flag=true;
        window.datelist.data.reverse();
    };
    while(window.datelist.strt_date>strt_date){
        window.datelist.strt_date-=1;
        window.datelist.data.push(indtodate(window.datelist.strt_date));
    }
    if(prepend_flag){
        window.datelist.data.reverse();
    };

    //append if strt_date+len is out of index
    let end_date=window.datelist.strt_date+window.datelist.data.length;
    while(end_date<strt_date+len){
        window.datelist.data.push(indtodate(end_date));
        end_date+=1;
    }

    //return the slice
    let strt_ind=strt_date-window.datelist.strt_date;
    return window.datelist.data.slice(strt_ind,strt_ind+len);
}

async function mainfetchDB(){
    try{
        let request={"recent_players":10,"ticker__^GSPC":window.localdb_meta.__todayind-183};
        Object.keys(window.localdb).forEach((key)=>{
            request[key]=window.localdb[key].end_date-1;
        });
        const response_json = await fetchDB(request);
        return response_json;
    }
    catch(err){
        console.error(err);
        return null;
    }
}