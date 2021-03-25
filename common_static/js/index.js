$(document).ready(function() {
//protein pdb type, hidden pdbxyz
    $("#id_pdbFileType_0").click(
        function () {
            $("#pdbXYZ").css("display", "none")
        }
    );

    $("#id_pdbFileType_1").click(
        function () {
            $("#pdbXYZ").css("display", "block")
        }
    );
})

window.alert = function(content) {
	// 做个弹窗元素
    const alertBox = document.createElement("alertBox");
    alertBox.id = "alert";
    let innerHTMLText = "<div class=\"alert-box\">\n";
	innerHTMLText += "<h5>"
    innerHTMLText += content
    innerHTMLText += "</h5>\n";
	innerHTMLText += "<div class=\"btn-area\">\n";
	innerHTMLText += "<input type=\"button\" value=\"OK\" onclick=\"removeAlertBox()\" />\n";
	innerHTMLText += "</div>\n";
	innerHTMLText += "</div>\n";
	alertBox.innerHTML = innerHTMLText;
	// 把这个元素加到页面里

    const bodyEle = document.getElementsByTagName("body")[0]
	bodyEle.appendChild(alertBox);
	// 点OK的时候删除这个元素
	this.removeAlertBox = function() {
		bodyEle.removeChild(alertBox);
	};

	// 用setTimeout来做一个定时器
    setTimeout(() => {
		bodyEle.removeChild(alertBox);
    }, 3000);
}

function checkInputStringAndFile() {
    // check textarea, inputFile
    const textarea = document.querySelector("#id_inputStr");
    const uploadInputFile = document.querySelector("#id_uploadInputFile")

    if (textarea.value == "" && uploadInputFile.value == "") {
        alert('Please, type in the blank of input string or select an input file')
        return false
    }
    return true
}

function submitPlaceHolderInInputString() {
    // check textarea, inputFile
    const textarea = document.querySelector("#id_inputStr");

    if (textarea.value == "") {
        textarea.value = textarea.placeholder
    }
    return true
}


function checkAllInput() {

    // checkbox
    const container = document.querySelector("#id_modelTypes");


    if (container !== null) {
        const checkboxGroup = container.querySelectorAll("input[type='checkbox']");
        let selectAtLeastOne = false
        for (let i = 0; i < checkboxGroup.length; i++) {
            if (checkboxGroup[i].checked === true) {
                selectAtLeastOne = true
            }
        }
        if (!selectAtLeastOne) {
            alert('Please, select at least one AI model type!')
            return false;
        }
    }
    return submitPlaceHolderInInputString()
}

function initialInputElements() {
    document.getElementById("id_inputStr").placeholder = "CN(C)C(=N)NC(N)=NCC(=O)OC1=CC=CC=C1C(O)=O"
    //raw smiles
    document.querySelector("#id_inputType_1").onclick = function () {
        document.getElementById("id_inputStr").placeholder="CN(C)C(=N)NC(N)=NCC(=O)OC1=CC=CC=C1C(O)=O"
    }
    document.querySelector("#id_inputType_0").onclick = function () {
        document.getElementById("id_inputStr").placeholder="metformin\n" + "aspirin"
    }
}
