function get_chat(channel){
  $.ajax({
    type: "POST",
    url:"/get_chat/",
    data:{
      channel: channel,
      "csrfmiddlewaretoken":csrftoken
    },
  success: function(data){
    document.getElementById("woy").innerHTML = data;
    }});

}

function get_list_chat(){
  $.ajax({
    type: "GET",
    url: "/get_list_chat/",
    data:{
    },
success: function(data){
  document.getElementById("chats").innerHTML = data;
}});
}

function add_contact(){
  var username=document.getElementById("name").value;
  var pin=document.getElementById("pin").value;
  $.ajax({
    type: "POST",
    url:"/send_contact/",
    data:{
      name:username,
      pin:pin,
      "csrfmiddlewaretoken":csrftoken
    },
  success: function(data){
    alert(data);
  }})
}

function send_message(){
  var message = document.getElementById("message").value;
  var time = new Date().toLocaleString();
  console.log("sent");
  $.ajax({
    type:"POST",
    url:"/send_message/",
    data:{
      channel:current_channel,
      message:message,
      time:time,
      "csrfmiddlewaretoken":csrftoken
    },
    success:function(data){
    }})
}

function seen(id){
  $.ajax({
type:"POST",
url:"/seen_message/",
data:{
channel_id: id,
"csrfmiddlewaretoken":csrftoken
},
success:function(data){
}})
}


