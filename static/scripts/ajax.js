var current_reply="";
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

function delete_chat(channel){
  $.ajax({
type: "POST",
url: "/delete_chat/",
data:{
channel:channel,
"csrfmiddlewaretoken":csrftoken
},
success: function(data){
}});
}

function get_list_chat(){
  if (search){
    $.ajax({
    type: "GET",
    url: "/get_list_chat/",
    data:{
      sort: document.getElementById("sort").value,
      query: document.getElementById("search").value
    },
    success: function(data){
      console.log(data);
      document.getElementById("chats").innerHTML = data;
    }
    });
    search=false;
    console.log("here");
    return;
  }

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

function delete_message(id){
  $.ajax({
    type:"POST",
    url:"/delete_message/",
    data:{
      id:id,
      channel:current_channel,
      "csrfmiddlewaretoken":csrftoken
    },
    success: function(data){
    }});
}

function send_message(){
  var message;
  if (current_reply != ""){
    message = current_reply+"\n"+document.getElementById("message").value;
  }
  else{
    message = document.getElementById("message").value;
  }
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
  current_reply="";
  document.getElementById("message").value="";
  document.getElementById("message").placeholder="Type a message...";
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


