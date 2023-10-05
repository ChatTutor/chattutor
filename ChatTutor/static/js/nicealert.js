var nicealert = document.getElementById("nice-alert")


export function alert(message, success=0) {
    nicealert.querySelector("span").innerHTML = message
    let classes = ["fail", "default", "success"]
    classes.forEach(el=>{
        nicealert.querySelector(".type").classList.remove(classes)
    })
    nicealert.querySelector(".type").classList.add = classes[success + 1]
    nicealert.classList.add("show")
    document.querySelector("#body-overlay").classList.add("show")

    nicealert.querySelector(".close").addEventListener("click", (e)=>{
        nicealert.classList.remove("show")
        document.querySelector("#body-overlay").classList.remove("show")

    })

}