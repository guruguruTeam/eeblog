menu=()=>{
    width=Math.ceil($(".list").width())
    size=parseInt($("body").css("font-size"))
    $("body").css("padding-right",$(".list").toggle().is(":visible")?`${width/size+8}em`:`${width/size-8}em`)
}
getDate=(time)=>{
    return new Date(time*1000).toLocaleString()
}
makeArchive=()=>{
    temp=data[0].reverse()
    list=temp.map((value)=>getDate(value[1]).split("/",3).slice(0,2).join("/"))
    Array.from(new Set(list)).forEach((value)=>{
        $(`<div class="item" date="${value}">`).append(
            $("<p class='level2'>").click(function () {
                $(this).nextAll().slideToggle()
            }).text(value)
        ).appendTo($(".list"))
    })
    list.forEach((value,index)=>{
        $(`div[date="${value}"]`).append(
            $('<div class="item">').append(
                $(`<a class="level3" href="/notes/${temp[index][0]}"></a>`).text(temp[index][0])
            )
        )
    })
}
makePage=()=>{
    temp=0
    page=parseInt(window.location.href.split("#")[1])
    data[1].reverse().forEach((value)=>{
        $("#header").prepend(`<li><a href="/pages/${value}">${value}</a></li> `)
    })
    for (i=1;i<=Math.ceil(data[0].length/5);i++) {
        div=$(`<div id="${i}">`).appendTo($("#essays"))
        temp_=temp
        if (i==page) div.addClass("now")
        for (temp;temp<Math.min(temp_+5,data[0].length);temp++) {
            makeEssay(data[0][temp]).appendTo(div)
        }
    }
    if ($(".now").length==0) {
        $($("#essays>div")[0]).addClass("now")
        window.location.href="#1"
    }
}
makeEssay=(value)=>{
    return $(`<div class="essay">`).append(
        $("<h2>").text(value[0]),
        $("<p>").html(`更新时间｜<u><i>${getDate(value[1])}</i></u>`)
    ).click(()=>window.location.href=`/notes/${value[0]}`)
}
makeSidebar=(index,value,delay)=>{
    setTimeout(()=>value.fadeIn(delay),(delay/4)*index)
}
randomEssay=()=>{
    window.location.href=`/notes/${data[0][Math.floor(Math.random()*data.length)][0]}`
}
firstPage=()=>{
    id=$(".now").attr("id")
    if (id!="1") {
        $(".now").removeClass("now")
        $("#1").addClass("now")
        window.location.href="#1"
    }
}
changePage=(num)=>{
    id=$(".now").attr("id")
    oh=num>0?$("#essays>div").length:"1"
    if (id!=oh) {
        $(".now").removeClass("now")
        $(`#${parseInt(id)+num}`).addClass("now")
        window.location.href=`#${parseInt(id)+num}`
    }
}
lastPage=()=>{
    id=$(".now").attr("id")
    max=$("#essays>div").length
    if (id!=max) {
        $(".now").removeClass("now")
        $(`#${$("#essays>div").length}`).addClass("now")
        window.location.href=`#${max}`
    }
}
$(document).ready(()=>{
    makePage()
    makeArchive()
    pangu.autoSpacingPage()
    setTimeout(()=>{
        $("body").fadeIn(1000)
        $(".list").fadeIn()
        $(window).scrollTop(parseFloat(localStorage.getItem("scroll"))).on("scroll",function () {
            localStorage.setItem("scroll",$(this).scrollTop())
        })
    },800)
})