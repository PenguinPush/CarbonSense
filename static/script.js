const shoppingIcon = document.getElementsById("shopping_cart");
const homeIcon = document.getElementsById("home");
const busIcon = document.getElementsById("bus");

console.log("wow!")

function redirect(link){
    console.log("wow!")
    window.location.href(link)
}

shoppingIcon.addEventListener("click", function(){
    console.log("wow!")
    redirect("/shopping")
});

homeIcon.addEventListener("click", function(){
    console.log("wow!")
    redirect("/")
});

transitIcon.addEventListener("click", function(){
    console.log("wow!")
    redirect("/transit")
});