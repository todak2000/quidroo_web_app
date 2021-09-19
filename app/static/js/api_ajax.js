function selectUser(id) {
    let blue = document.getElementById("blue");
    let red = document.getElementById("red");
    let green = document.getElementById("green");
    let nextBtn = document.getElementById("btn-nxt");
    if(id === "blue"){
        red.classList.remove("red-selected");
        green.classList.remove("green-selected");
        blue.classList.add("blue-selected");
        nextBtn.disabled = false
        nextBtn.classList.remove("btn-disabled");
        nextBtn.classList.add("btn-nxt");
    }
    if(id === "red"){
        blue.classList.remove("blue-selected");
        green.classList.remove("green-selected");
        red.classList.add("red-selected");
        nextBtn.disabled = false
        nextBtn.classList.remove("btn-disabled");
        nextBtn.classList.add("btn-nxt");
    }
    if(id === "green"){
        blue.classList.remove("blue-selected");
        red.classList.remove("red-selected");
        green.classList.add("green-selected");
        nextBtn.disabled = false
        nextBtn.classList.remove("btn-disabled");
        nextBtn.classList.add("btn-nxt");
    }
    console.log(id);
}


