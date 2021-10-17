$(function(){
    $('#ic_btn-continue').on('click', function (e) {
        e.preventDefault();
        let formOne = document.getElementById("ic_form-inner-one");
        let formTwo = document.getElementById("ic_form-inner-two");
        formOne.classList.add("disappeared");
        formOne.classList.remove("appear");
        formTwo.classList.add("appear");
        formTwo.classList.remove("disappeared");
})})

$(function(){
    $('#ver_btn-back-one').on('click', function (e) {
        e.preventDefault();
        let formOne = document.getElementById("ver_form-inner-one");
        let formTwo = document.getElementById("ver_form-inner-two");
        formOne .classList.add("appear");
        formTwo.classList.add("disappeared");
})})

function verification_checkFormOne() {
    let file= document.getElementById("file_id");
    let file_display= document.getElementById("file_display_id");
    
    let cac_cert= document.getElementById("cac_cert");
    let cac_cert_display = document.getElementById("cac_cert_display");
    let bank_statement= document.getElementById("bank_statement");
    let bank_statement_display = document.getElementById("bank_statement_display");
    if(file.value !== "" || cac_cert.value !== "" || bank_statement.value !== ""){
        file_display.value = file.value
        cac_cert_display.value = cac_cert.value;
        bank_statement_display.value = bank_statement.value;

        // let fileing = $("#file_id")[0].files[0]; 
        // file_display.value = fileing.name;
        // let cacing = $("#cac_cert")[0].files[0]; 
        // cac_cert_display.value = cacing.name;
        // let banking = $("#bank_statement")[0].files[0]; 
        // bank_statement_display.value = banking.name;
        
    }
    let tin_no= document.getElementById("tin_no");
    let nin_no = document.getElementById("nin_no");
    let contBtn = document.getElementById("ver_btn-continue");
    
    if (file.value !== "" && cac_cert.value !== "" && bank_statement.value !== "" && nin_no.value !== "" && tin_no.value !== ""){
        contBtn.disabled = false
        contBtn.classList.remove("btn-disabled");
        contBtn.classList.add("btn-create-account");
    }
    else{
        contBtn.disabled = true
        contBtn.classList.add("btn-disabled");
        contBtn.classList.remove("btn-create-account");
    }
}
function verification_checkFormTwo() {
    let verBank= document.getElementById("ver-bank");
    let verAcc = document.getElementById("ver-acc-no");
    let verAccName= document.getElementById("ver-acc-name");
    let verBvn = document.getElementById("ver-bvn");
    
    let contBtn = document.getElementById("activate-btn");
    
    if (verBank.value !== "" && verAcc.value !== "" && verAccName.value !== "" && verBvn.value !== "" ){
        contBtn.disabled = false
        contBtn.classList.remove("btn-disabled");
        contBtn.classList.add("btn-create-account");
    }
    else{
        contBtn.disabled = true
        contBtn.classList.add("btn-disabled");
        contBtn.classList.remove("btn-create-account");
    }
}
$(function(){
    $('#ver_btn-continue').on('click', function (e) {
        e.preventDefault();
        let formOne = document.getElementById("ver_form-inner-one");
        let formTwo = document.getElementById("ver_form-inner-two");
        formOne.classList.add("disappeared");
        formOne.classList.remove("appear");
        formTwo.classList.add("appear");
        formTwo.classList.remove("disappeared");

        let bankDetails = document.getElementById("bank-details");
        let documentation = document.getElementById("documentation");
        let bankBadge = document.getElementById("bank-badge");
        let docBadge = document.getElementById("doc-badge");

        bankDetails.classList.add("verification-active");
        bankDetails.classList.remove("verification-inactive");
        bankBadge.classList.add("badge-active");
        bankBadge.classList.remove("badge-inactive");

        documentation.classList.add("verification-green");
        documentation.classList.remove("verification-active");
        docBadge.classList.add("badge-green-ver");
        docBadge.classList.remove("badge-active");
})})