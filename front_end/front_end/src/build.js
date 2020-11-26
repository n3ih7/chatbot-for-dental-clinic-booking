function getCookie(name) {
    return (name = (document.cookie + ';').match(new RegExp(name + '=.*;'))) && name[0].split(/[=;]/)[1];
}

function findBodyAndEmpty() {
    let body = document.getElementById("main");
    while (body.firstChild) {
        body.removeChild(body.firstChild);
    }
    return body
}

function loadMainPage() {
    let body = findBodyAndEmpty();
    let container = document.createElement("div");
    container.style.marginTop = "20px";
    container.style.marginBottom = "20px";
    container.style.width = "500px";
    container.style.backgroundColor = "#ffffff";
    container.style.boxShadow = "0 2px 6px 0 rgba(0, 0, 0, 0.2)"
    container.style.borderRadius = "10px";
    let main = document.createElement("div");
    main.style.display = "flex";
    main.style.flexDirection = "column";
    main.style.padding = "0";

    let title = document.createElement("div");
    title.style.display = "flex";
    title.style.flexDirection = "row";
    title.style.padding = "15px 0 15px 0";
    title.style.marginBottom = "0";
    title.style.backgroundColor = "#4667a9";
    title.style.color = "white";
    title.style.borderRadius = "10px 10px 0 0";
    let botIcon = document.createElement("img");
    botIcon.src = "src/icon.png";
    botIcon.style.width = "25px";
    botIcon.style.height = "25px";
    botIcon.style.marginLeft = "0.5rem"
    let botName = document.createElement("div");
    botName.textContent = "Alfalfa";
    botName.style.fontSize = "15pt";
    botName.style.lineHeight = "16pt";
    botName.style.paddingTop = "3px"
    let botComment = document.createElement("div");
    botComment.textContent = "- your virtual assistant";
    botComment.style.paddingLeft = "5px"
    botComment.style.paddingTop = "6px"

    let chat_text = document.createElement("div");
    chat_text.style.display = "flex";
    chat_text.style.flexDirection = "column";
    chat_text.style.resize = "none";
    chat_text.style.overflowY = "scroll";
    chat_text.style.height = "545px";
    chat_text.style.borderBottom = "1px solid #d6d6d6";
    chat_text.style.display = "flex";
    chat_text.style.flexDirection = "column";
    chat_text.style.padding = "0 15px 0 10px";

    let input_text = document.createElement("div");
    input_text.style.height = "55px";
    input_text.style.display = "flex";
    input_text.style.flexDirection = "row";
    let input = document.createElement("input");
    input.style.height = "45px";
    input.style.width = "415px";
    input.style.lineHeight = "45px";
    input.style.outline = "none";
    input.style.border = "none";
    input.style.borderWidth = "0";
    input.placeholder = "Enter text here";
    input.style.boxShadow = "none";
    input.style.fontSize = "15pt";
    input.style.marginLeft = "15px";
    input.style.paddingTop = "5px";
    input.addEventListener("keyup", function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            arrowIcon.click();
        }
    });
    let arrowIcon = document.createElement("img");
    arrowIcon.src = "src/noun_right_arrow_button_581650.png";
    arrowIcon.style.width = "40px";
    arrowIcon.style.height = "40px";
    arrowIcon.style.paddingTop = "8px"
    arrowIcon.style.paddingLeft = "10px"
    arrowIcon.addEventListener("click", () => {
        if (input.value !== '') {
            let msg = input.value;
            input.value = '';
            let sent_msg_json = {
                msg_source: "user",
                msg: msg,
                timestamp: Date.now().toString()
            };
            // console.log(sent_msg_json);
            renderResult(chat_text, sent_msg_json);

            (async () => {
                const rawResponse = await fetch('http://127.0.0.1:8001/ask', {
                    // mode: 'cors',
                    cache: "no-cache",
                    method: 'POST',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        msg_source: "user",
                        msg: msg
                    })
                });
                // console.log(rawResponse.headers);
                const content = await rawResponse.json();
                if (rawResponse["status"] !== 200) {
                    console.warn(`API_ERROR: ${content.message}`);
                } else {
                    // console.log(content);
                    renderResult(chat_text, content);
                }
            })();
        }
    })

    title.appendChild(botIcon);
    title.appendChild(botName);
    title.appendChild(botComment);
    input_text.appendChild(input);
    input_text.appendChild(arrowIcon);
    main.appendChild(title);
    main.appendChild(chat_text);
    main.appendChild(input_text);
    container.appendChild(main);
    body.appendChild(container);
}

function renderResult(container, json) {
    if (json['msg_source'] === "bot") {
        let bot_msg = document.createElement("div");
        bot_msg.style.display = "flex";
        bot_msg.style.flexDirection = "column";
        bot_msg.style.marginTop = "5px";
        let chat_timestamp = document.createElement("div");
        const d = new Date(parseInt(json['timestamp'])).toLocaleString('en-AU', {
            hour: "2-digit",
            minute: "2-digit"
        });
        chat_timestamp.textContent = "Alfalfa - " + d;
        chat_timestamp.style.color = "#848485";
        chat_timestamp.style.fontSize = "11pt";
        chat_timestamp.style.paddingLeft = "5px";
        let msg_line2 = document.createElement("div");
        msg_line2.style.display = "flex";
        msg_line2.style.flexDirection = "row";
        let line2_left = document.createElement("div");
        line2_left.style.display = "flex";
        line2_left.style.flexDirection = "column-reserve";
        let bot_chat_icon = document.createElement("img");
        bot_chat_icon.src = "src/Codi-Avatar-200px.png";
        bot_chat_icon.style.width = "40px";
        bot_chat_icon.style.height = "40px";
        bot_chat_icon.style.alignSelf = "flex-end";
        let msg_div = document.createElement("div");
        msg_div.style.marginTop = "5px";
        msg_div.style.marginLeft = "8px";
        msg_div.style.marginBottom = "8px";
        msg_div.style.padding = "5px 10px 5px 10px";
        msg_div.style.backgroundColor = "#4667a9";
        msg_div.style.lineHeight = "17pt";
        msg_div.style.color = "white";
        msg_div.style.fontWeight = "normal";
        msg_div.innerHTML = json['msg'];
        msg_div.style.maxWidth = "350px";
        bot_msg.appendChild(chat_timestamp);
        msg_line2.appendChild(line2_left);
        line2_left.appendChild(bot_chat_icon)
        msg_line2.appendChild(msg_div)
        bot_msg.appendChild(msg_line2);
        container.appendChild(bot_msg);
        container.scrollTop = container.scrollHeight;
    }

    if (json['msg_source'] === "user") {
        let bot_msg = document.createElement("div");
        bot_msg.style.display = "flex";
        bot_msg.style.flexDirection = "column";
        bot_msg.style.alignItems = "flex-end";
        bot_msg.style.marginTop = "5px";
        let chat_timestamp = document.createElement("div");
        const d = new Date(parseInt(json['timestamp'])).toLocaleString('en-AU', {
            hour: "2-digit",
            minute: "2-digit"
        });
        chat_timestamp.textContent = "You - " + d;
        chat_timestamp.style.color = "#848485";
        chat_timestamp.style.fontSize = "11pt";
        chat_timestamp.style.paddingLeft = "5px";
        let msg_div = document.createElement("div");
        msg_div.style.marginTop = "5px";
        msg_div.style.marginLeft = "8px";
        msg_div.style.marginBottom = "8px";
        msg_div.style.padding = "5px 10px 5px 10px";
        msg_div.style.backgroundColor = "#4667a9";
        msg_div.style.lineHeight = "17pt";
        msg_div.style.color = "white";
        msg_div.style.fontWeight = "normal";
        msg_div.textContent = json['msg'];
        msg_div.style.maxWidth = "350px";
        bot_msg.appendChild(chat_timestamp);
        bot_msg.appendChild(msg_div);
        container.appendChild(bot_msg);
        container.scrollTop = container.scrollHeight;
    }

}

window.onload = function () {
    loadMainPage();
}