    function checkAllInput() {
        // checkbox
        const container = document.querySelector("#id_modelTypes");
        const checkboxGroup = container.querySelectorAll("input[type='checkbox']");
        let selectAtLeastOne = false
        for (let i = 0; i < checkboxGroup.length; i++) {
            if (checkboxGroup[i].checked === true) {
                selectAtLeastOne = true
            }
        }
        if (!selectAtLeastOne) {
            alert('Please, select at least one AI model type!')
            return false
        }
        // check textarea, inputFile
        const textarea = document.querySelector("#id_inputStr");
        const uploadInputFile = document.querySelector("#id_uploadInputFile")

        if (textarea.value == "" && uploadInputFile.value == "") {
            alert('Please, type in the blank of input string or select an input file')
            return false
        }

    }