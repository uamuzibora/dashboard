
function data(){
    jdata=[]
    var request=$.post("http://localhost/backend",
	   {
	       data:"all",request_type:"dashboard"
	   },
	   function(data,status){
	       jdata=jQuery.parseJSON(data);
	       alert("hei")
	       alert(jdata)
	   })
	.done(function(){load_numbers()});
    return jdata
}