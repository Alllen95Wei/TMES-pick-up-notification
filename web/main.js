$(document).ready(function () {
    let wsUrl = configServerUrl()

    const WS = new WebSocket(wsUrl);
    $("#wsUrlDisplay").text(wsUrl);

    WS.onopen = function () {
        $("#wsUrlDisplay").css("color", "green");
        WS.send(JSON.stringify({
            "type": "INIT",
            "classNo": 777
        }))
        $("#header").prepend("<h1 id=\"title\" style=\"font-size: 5ex; \">我是標題-首頁</h1>")

    }

    WS.onerror = function (e) {
        console.error(e);
        alert("與伺服器連接失敗。請嘗試重新整理網頁，或檢查伺服器位址是否正確。");
        $("#wsUrlDisplay").css("color", "red");
    }

    WS.onclose = function (e) {
        if (e.code > 1001 && e.code !== 1006) {
            alert(`與伺服器的連線中斷。請嘗試重新整理網頁，或檢查伺服器位址是否正確。\n錯誤代碼：${e.code}`)
        }
        $("#wsUrlDisplay").css("color", "red");
    }


    WS.onmessage = function (event) {
        const data = JSON.parse(event.data);
        const clsArray = data["students"];
        $(".btn").on("click", function () {
            const targetClsNo = parseInt(this.id);
            const studentArray = clsArray[parseInt(this.id)]
            if (data["type"] === "STUDENT_LIST") {
                $.each(studentArray, function (index, value) {
                    console.log(value);
                    const clsNum = value["classNo"];
                    const seatNum = value["seatNo"];
                    const name = value["name"];
                    const butMode = document.createElement("input");
                    butMode.type = "button";
                    butMode.id = clsNum + "-" + seatNum;
                    butMode.className = "btn2";
                    butMode.value = clsNum + "-" + seatNum + name;
                    $("#btnGroup").append(butMode);
                    $(`#${clsNum}-${seatNum}`).click(function (event) {
                        const cls = this.id.slice(0, this.id.indexOf("-"));
                        const num = this.id.slice(this.id.indexOf("-") + 1, this.id.length);
                        const Name = this.value.slice(this.id.length, this.value.length);
                        WS.send(JSON.stringify({
                            "type": "CALL_FOR_STUDENT",
                            "targetClassNo": targetClsNo,
                            "students": {
                                "classNo": cls,
                                "seatNo": num,
                                "name": Name
                            }
                        }))
                        alert(`已通知 ${cls}-${num}${Name}`)
                    })
                })
            }
        })
        if (data["type"] === "CALL_FOR_STUDENT") {
            const date = new Date();
            const currentTime = date.toLocaleDateString() + " " + date.toLocaleTimeString();
            const studentDic = data["students"];
            console.log(studentDic);
            const clsNum = studentDic["classNo"];
            const seatNum = studentDic["seatNo"];
            const name = studentDic["name"];
            // const comfirmBtn = document.createElement("input");
            // comfirmBtn.type = "button";
            // comfirmBtn.className = "confirmBtn";
            // comfirmBtn.id = "confirmBtn" + clsNum + "-" + seatNum;
            // comfirmBtn.value = "確認";
            $("#student-call").prepend(`<div id="${clsNum}-${seatNum}" class="calledDiv"><h2>${clsNum}-${seatNum}${name}</h2><button id="confirmBtn${clsNum}-${seatNum}" class="confirmBtn" onclick="function confirmBtn() {}">確認</button><p>${currentTime}</p></div>`)
            document.getElementById(`confirmBtn${clsNum}-${seatNum}`).addEventListener("click", function () {
                $(`${this.id.slice(10,this.id.length)}`).css("border","#00dc01");
                console.log(`${this.id.slice(10,this.id.length)}`)})
        }
    }
    let classNum = "";
    let body = $("body");
    body.css("background-color", "pink");
    $(".btn").click(function () {
        classNum = this.id;
        console.log(classNum);
        $("#btnGroup").empty();
        $("#btnGroup").prepend(`<button class="clsBtn" id="classroom-${classNum}">${classNum}教室端</button>`)
        $(".clsBtn").click(function () {
            $("#title").remove();
            $("#header").prepend(`<h1 id=\"title" style=\"font-size: 5ex; \">我是標題-${this.id.slice(this.id.indexOf("-") + 1, this.id.length)}教室</h1>`);
            console.log(this.id);
            $(".btn").hide();
            $("#btnGroup").hide();
            WS.send(JSON.stringify({
                "type": "INIT",
                "classNo": parseInt(this.id.slice(this.id.indexOf("-") + 1, this.id.length))
            }))
        })
        $("#backhome").click(function () {
            window.location.reload();
        })

    })

})

$("#clearStorageUrl").on("click", function () {
    window.localStorage.removeItem("wsUrl");
    configServerUrl();
    window.location.reload();
})

function configServerUrl() {
    const storage = window.localStorage;
    let wsUrl = storage.getItem("wsUrl");
    if (wsUrl === null) {
        wsUrl = prompt("請輸入伺服器端的 IP 及端口 (如：ws://localhost:8001)");
        storage.setItem("wsUrl", wsUrl);
    }

    return wsUrl;
}
