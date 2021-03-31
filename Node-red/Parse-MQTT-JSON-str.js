var pTopic  = msg.topic.split("/");
var jsonObj   =JSON.parse(msg.payload);
var fields = {};
var tags = {location:pTopic[0], device:pTopic[1]};
for(var item in jsonObj){
    if (item.endsWith('f')) {
        fields[item] = parseFloat(jsonObj[item]);
    }
    if (item.endsWith('i')) {
        fields[item] = parseInt(jsonObj[item]);
    }
}
msg.payload = [
    fields,
    tags
];    
return msg;