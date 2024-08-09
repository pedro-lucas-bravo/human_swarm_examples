
inlets = 1;
outlets = 1;

function list(val)
{
    if(arguments.length % 3 == 0){
        for (var i = 0; i < arguments.length; i+=3){
            var receiverId = arguments[i];
            var senderId = arguments[i+1];
            var message = arguments[i+2];
            //post("Receiver: " + receiverId + " Sender: " + senderId + " Message: " + message + "\n")
            outlet(0, "target",receiverId);
            outlet(0, parseInt(message));
        }
    }
}