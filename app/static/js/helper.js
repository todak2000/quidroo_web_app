
function s_checkFormOne() {
    let company = document.getElementById("s_company");
    let address = document.getElementById("s_address");
    let cac = document.getElementById("s_cac");
    let contBtn = document.getElementById("s_btn-continue");
    if (company.value !== "" && address.value !== "" && cac.value !== ""){
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

function v_checkFormOne() {
    let company = document.getElementById("v_company");
    let address = document.getElementById("v_address");
    let cac = document.getElementById("v_cac");
    let contBtn = document.getElementById("v_btn-continue");
    if (company.value !== "" && address.value !== "" && cac.value !== ""){
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
function ic_checkFormOne() {
    let company = document.getElementById("ic_company_name");
    let address = document.getElementById("ic_address");
    let cac = document.getElementById("ic_cac");
    let contBtn = document.getElementById("ic_btn-continue");
    console.log(company.value)
    if (company.value !== "" && address.value !== "" && cac.value !== ""){
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
function ii_checkFormOne() {
    let name= document.getElementById("ii_name");
    let address = document.getElementById("ii_address");
    let email = document.getElementById("ii_email");
    let contBtn = document.getElementById("ii_btn-continue");
    if (name.value !== "" && address.value !== "" && email.value !== ""){
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
function el_checkFormOne() {
    let password= document.getElementById("el_password");
    
    let email = document.getElementById("el_email");
    let contBtn = document.getElementById("el_btn-login");
    if (password.value !== "" && email.value !== ""){
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
function l_checkFormOne() {
    let password= document.getElementById("l_password");
    
    let email = document.getElementById("l_email");
    let contBtn = document.getElementById("l_btn-login");
    if (password.value !== "" && email.value !== ""){
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
function f_checkFormOne() {
    let email = document.getElementById("f_email");
    let contBtn = document.getElementById("f_btn-continue");
    if ( email.value !== ""){
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
function r_checkFormOne() {
    let password = document.getElementById("r_password");
    let contBtn = document.getElementById("r_btn-continue");
    if ( password.value !== ""){
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
function rl_checkFormOne() {
    let password= document.getElementById("rl_password");
    
    let email = document.getElementById("rl_email");
    let contBtn = document.getElementById("rl_btn-login");
    if (password.value !== "" && email.value !== ""){
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
function s_showPassword() {
    let x = document.getElementById("s_password");
    let showIcon = document.getElementById("s_show_eye");
    let hideIcon = document.getElementById("s_hide_eye");
    if (x.type === "password") {
      x.type = "text";
      showIcon.style.display = "none";
      hideIcon.style.display = "block";
    } else {
      x.type = "password";
      showIcon.style.display = "block";
      hideIcon.style.display = "none";
    }
}
function v_showPassword() {
    let x = document.getElementById("v_password");
    let showIcon = document.getElementById("v_show_eye");
    let hideIcon = document.getElementById("v_hide_eye");
    if (x.type === "password") {
      x.type = "text";
      showIcon.style.display = "none";
      hideIcon.style.display = "block";
    } else {
      x.type = "password";
      showIcon.style.display = "block";
      hideIcon.style.display = "none";
    }
}
function ic_showPassword() {
    let x = document.getElementById("ic_password");
    let showIcon = document.getElementById("ic_show_eye");
    let hideIcon = document.getElementById("ic_hide_eye");
    if (x.type === "password") {
      x.type = "text";
      showIcon.style.display = "none";
      hideIcon.style.display = "block";
    } else {
      x.type = "password";
      showIcon.style.display = "block";
      hideIcon.style.display = "none";
    }
}
function ii_showPassword() {
    let x = document.getElementById("ii_password");
    let showIcon = document.getElementById("ii_show_eye");
    let hideIcon = document.getElementById("ii_hide_eye");
    if (x.type === "password") {
      x.type = "text";
      showIcon.style.display = "none";
      hideIcon.style.display = "block";
    } else {
      x.type = "password";
      showIcon.style.display = "block";
      hideIcon.style.display = "none";
    }
}
function el_showPassword() {
    let x = document.getElementById("el_password");
    let showIcon = document.getElementById("el_show_eye");
    let hideIcon = document.getElementById("el_hide_eye");
    if (x.type === "password") {
      x.type = "text";
      showIcon.style.display = "none";
      hideIcon.style.display = "block";
    } else {
      x.type = "password";
      showIcon.style.display = "block";
      hideIcon.style.display = "none";
    }
}
function l_showPassword() {
    let x = document.getElementById("l_password");
    let showIcon = document.getElementById("l_show_eye");
    let hideIcon = document.getElementById("l_hide_eye");
    if (x.type === "password") {
      x.type = "text";
      showIcon.style.display = "none";
      hideIcon.style.display = "block";
    } else {
      x.type = "password";
      showIcon.style.display = "block";
      hideIcon.style.display = "none";
    }
}
function r_showPassword() {
    let x = document.getElementById("r_password");
    let showIcon = document.getElementById("r_show_eye");
    let hideIcon = document.getElementById("r_hide_eye");
    if (x.type === "password") {
      x.type = "text";
      showIcon.style.display = "none";
      hideIcon.style.display = "block";
    } else {
      x.type = "password";
      showIcon.style.display = "block";
      hideIcon.style.display = "none";
    }
}
function rl_showPassword() {
    let x = document.getElementById("rl_password");
    let showIcon = document.getElementById("rl_show_eye");
    let hideIcon = document.getElementById("rl_hide_eye");
    if (x.type === "password") {
      x.type = "text";
      showIcon.style.display = "none";
      hideIcon.style.display = "block";
    } else {
      x.type = "password";
      showIcon.style.display = "block";
      hideIcon.style.display = "none";
    }
}
function selectUser(id) {
    let blue = document.getElementById("blue");
    let red = document.getElementById("red");
    let green = document.getElementById("green");
    let nextBtn = document.getElementById("btn-nxt");
    let conti = document.getElementById("continue");
    if(id === "blue"){
        red.classList.remove("red-selected");
        green.classList.remove("green-selected");
        blue.classList.add("blue-selected");
        nextBtn.disabled = false
        nextBtn.classList.remove("btn-disabled");
        nextBtn.classList.add("btn-nxt");
        conti.value = "seller"
    }
    if(id === "red"){
        blue.classList.remove("blue-selected");
        green.classList.remove("green-selected");
        red.classList.add("red-selected");
        nextBtn.disabled = false
        nextBtn.classList.remove("btn-disabled");
        nextBtn.classList.add("btn-nxt");
        conti.value = "vendor"
    }
    if(id === "green"){
        blue.classList.remove("blue-selected");
        red.classList.remove("red-selected");
        green.classList.add("green-selected");
        nextBtn.disabled = false
        nextBtn.classList.remove("btn-disabled");
        nextBtn.classList.add("btn-nxt");
        conti.value = "investor"
    }
    // console.log(id);
}


$(function(){
    $('#btn-nxt').on('click', function (e) {
        e.preventDefault();
        let conti = document.getElementById("continue");
        let index = document.getElementById("index");
        let seller = document.getElementById("seller");
        let vendor = document.getElementById("vendor");
        let investor = document.getElementById("investor");
        if (conti.value == "seller"){
            index.classList.add("disappear");
            index.classList.remove("appear");
            seller.classList.add("appear");
            seller.classList.remove("disappear");
            console.log("seller")
        }
        else if (conti.value == "investor"){
            index.classList.add("disappear");
            index.classList.remove("appear");
            investor.classList.add("appear");
            investor.classList.remove("disappear");
            console.log("investor")
        }
        else if (conti.value == "vendor"){
            index.classList.add("disappear");
            index.classList.remove("appear");
            vendor.classList.add("appear");
            vendor.classList.remove("disappear");
            console.log("vendor")
        }
        else{
            console.log("error in page selection")
        }

        // window.location.reload();
    
    })});

    $(function(){
        $('#s_btn-back-index').on('click', function (e) {
            e.preventDefault();
            let index = document.getElementById("index");
            let seller = document.getElementById("seller");
            index.classList.add("appear");
            seller.classList.add("disappear");
            seller.classList.remove("appear");
    })})
    $(function(){
        $('#v_btn-back-index').on('click', function (e) {
            e.preventDefault();
            let index = document.getElementById("index");
            let vendor = document.getElementById("vendor");
            index.classList.add("appear");
            vendor.classList.add("disappear");
            vendor.classList.remove("appear");
    })})
    $(function(){
        $('#ic_btn-back-index').on('click', function (e) {
            e.preventDefault();
            let index = document.getElementById("index");
            let investor = document.getElementById("investor");
            index.classList.add("appear");
            investor.classList.add("disappear");
            investor.classList.remove("appear");
    })})
    $(function(){
        $('#ii_btn-back-index').on('click', function (e) {
            e.preventDefault();
            let index = document.getElementById("index");
            let investor = document.getElementById("investor");
            index.classList.add("appear");
            investor.classList.add("disappear");
            investor.classList.remove("appear");
    })})

    $(function(){
        $('#s_diff_account').on('click', function (e) {
            e.preventDefault();
            let index = document.getElementById("index");
            let seller = document.getElementById("seller");
            index.classList.add("appear");
            seller.classList.add("disappear");
            seller.classList.remove("appear");
    })})
    $(function(){
        $('#v_diff_account').on('click', function (e) {
            e.preventDefault();
            let index = document.getElementById("index");
            let vendor = document.getElementById("vendor");
            index.classList.add("appear");
            vendor.classList.add("disappear");
            vendor.classList.remove("appear");
    })})
    $(function(){
        $('#ic_diff_account').on('click', function (e) {
            e.preventDefault();
            let index = document.getElementById("index");
            let investor = document.getElementById("investor");
            index.classList.add("appear");
            investor.classList.add("disappear");
            investor.classList.remove("appear");
    })})
    $(function(){
        $('#ii_diff_account').on('click', function (e) {
            e.preventDefault();
            let index = document.getElementById("index");
            let investor = document.getElementById("investor");
            index.classList.add("appear");
            investor.classList.add("disappear");
            investor.classList.remove("appear");
    })})

    $(function(){
        $('#s_btn-continue').on('click', function (e) {
            e.preventDefault();
            let formOne = document.getElementById("s_form-inner-one");
            let formTwo = document.getElementById("s_form-inner-two");
            formOne.classList.add("disappear");
            formOne.classList.remove("appear");
            formTwo.classList.add("appear");
            formTwo.classList.remove("disappear");
    })})
    $(function(){
        $('#v_btn-continue').on('click', function (e) {
            e.preventDefault();
            let formOne = document.getElementById("v_form-inner-one");
            let formTwo = document.getElementById("v_form-inner-two");
            formOne.classList.add("disappear");
            formOne.classList.remove("appear");
            formTwo.classList.add("appear");
            formTwo.classList.remove("disappear");
    })})
    $(function(){
        $('#ic_btn-continue').on('click', function (e) {
            e.preventDefault();
            let formOne = document.getElementById("ic_form-inner-one");
            let formTwo = document.getElementById("ic_form-inner-two");
            formOne.classList.add("disappear");
            formOne.classList.remove("appear");
            formTwo.classList.add("appear");
            formTwo.classList.remove("disappear");
    })})
    $(function(){
        $('#ii_btn-continue').on('click', function (e) {
            e.preventDefault();
            let formOne = document.getElementById("ii_form-inner-one");
            let formTwo = document.getElementById("ii_form-inner-two");
            formOne.classList.add("disappear");
            formOne.classList.remove("appear");
            formTwo.classList.add("appear");
            formTwo.classList.remove("disappear");
    })})

    $(function(){
        $('#s_btn-back-one').on('click', function (e) {
            e.preventDefault();
            let formOne = document.getElementById("s_form-inner-one");
            let formTwo = document.getElementById("s_form-inner-two");
            formOne .classList.add("appear");
            formTwo.classList.add("disappear");
            formTwo.classList.remove("appear");
    })})
    $(function(){
        $('#v_btn-back-one').on('click', function (e) {
            e.preventDefault();
            let formOne = document.getElementById("v_form-inner-one");
            let formTwo = document.getElementById("v_form-inner-two");
            formOne .classList.add("appear");
            formTwo.classList.add("disappear");
            formTwo.classList.remove("appear");
    })})
    $(function(){
        $('#ic_btn-back-one').on('click', function (e) {
            e.preventDefault();
            let formOne = document.getElementById("ic_form-inner-one");
            let formTwo = document.getElementById("ic_form-inner-two");
            formOne .classList.add("appear");
            formTwo.classList.add("disappear");
            formTwo.classList.remove("appear");
    })})
    $(function(){
        $('#ii_btn-back-one').on('click', function (e) {
            e.preventDefault();
            let formOne = document.getElementById("ii_form-inner-one");
            let formTwo = document.getElementById("ii_form-inner-two");
            formOne .classList.add("appear");
            formTwo.classList.add("disappear");
            formTwo.classList.remove("appear");
    })})