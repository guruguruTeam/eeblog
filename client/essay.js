menu=()=>{
    width=Math.ceil($(".list").width())
    size=parseInt($("body").css("font-size"))
    $("body").css("padding-right",$(".list").toggle().is(":visible")?`${width/size+8}em`:`${width/size-8}em`)
}
markdown=(html)=>new Remarkable("full",{
    html:html,
    xhtmlOut:false,
    breaks:true,
    langPrefix:"",
    linkify:true,
    typographer:true,
    quotes:`""''`,
    doHighlight:false,
    linkTarget:'_blank" rel="noreferrer'
})
request=(url,data_)=>{
    pack={
        url:url,
        data:data_,
        type:"POST",
        cache:false,
        contentType:false,
        processData:false,
        success:(res)=>console.log(reload(res)),
        error:(jq,status,error)=>console.log(`${status}:${error}`),
    }
    console.log(pack)
    return pack
}
reload=(res)=>{
    if (res[1]=="评论") {
        if (res[0]) {
            $("#comments").prepend(makeComment(res[3]).hide().fadeIn())
        }
        $("#tips").text(res[2])
    }
    return res
}
makeComment=(data_)=>{
    return $("<div class='comment'>").append(
        $("<p>").html(`<b><i><f1>${data_[0]}</f1> <f0><u>${getDate(data_[2])}</u></f0></i></b>`),
        $("<div>").html(markdown(false).render(data_[1]))
    )
}
autoHeight=(dom)=>{
    $(dom).css("height",0)
    $(dom).css("height",$(dom)[0].scrollHeight+"px")
}
getDate=(time)=>{
    return new Date(time*1000).toLocaleString()
}
addText=(text)=>{
    $("#editText")[0].value+=text
}
addLavel=(dom)=>{
    $(dom).each(function (index) {
        $(this).attr("id",index+1).click(()=>window.location.href=`#${index+1}`)
    })
}
getChildren=(item,arr)=>{
    if (!item) return
    minus=-item.level
    children=[]
    for (i=0,len=arr.length;i<len;i++) {
        level=arr[i]
        if (-level.level<minus) {
            children.push(level)
        }
        else break
    }
    if (children.length>0) {
        arr.splice(0,children.length)
    }
    return children
}
getTree=(result,arr,level)=>{
    item=arr.shift()
    if (item) {
        item.level=level
        result.push(item)
    }
    while (arr.length>0) {
        if (!item) return
        children=getChildren(item,arr)
        if (!children.length) {
            item=arr.shift()
            if (item) {
                item.level=level
                result.push(item)
            }
            continue
        }
        item.children=[]
        getTree(item.children,children,level+1)
    }
}
getDomTree=(tree)=>{
    $(tree).each(function () {
        $(`<div class="item"><a class="level${this.level}" href="#${this.id}">${this.text}</a></>`).appendTo($(".list"))
        getDomTree(this.children)
    })
}
toTree=(arr)=>{
    level=1
    tree=[]
    copy=[].slice.call(arr).map((item)=>{
        return {
            ...item,
            level:item.nodeName.slice(1),
            text:item.textContent,
            id:item.id
        }
    })
    getTree(tree,copy,level)
    return tree
}
createToc=(dom)=>{
    TocList=$(dom).find("h1,h2,h3")
    addLavel(TocList)
    getDomTree(toTree(TocList))
}
$(document).ready(()=>{
    $("#editText").on("input",function () {
        autoHeight(this)
    })
    $("#forum").submit(function (event) {
        event.preventDefault()
        data_=new FormData(this)
        data_.append("note",data[1])
        data_.append("user",$("#editNick")[0].value||"")
        data_.append("content",$("#editText")[0].value||"")
        $.ajax(request("/comment",data_))
        $("#tips").text("评论正在发送中……")
        $("#editText")[0].value=""
    })
    $("#responses>p>a").click(function () {
        addText(` ${$(this).text()} `)
        autoHeight("#editText")
    })
    $("#editText").focusin(()=>$("#responses").slideDown(400)).focusout(()=>$("#responses").slideUp())
    if (data[0]=="notes") {
        $("#essay").append(
            $("<h1>").text("笔记信息"),
            $("<p>").html(`<b>《${data[1]}》</b>`),
            $("<p>").html(`<p>更新时间｜<u><i>${getDate(data[3])}</i></u>`),
            $("<p>").html(`共有<i>${data[2].length}</i>字 预计阅读时长<i>${Math.ceil(data[2].length/500)}</i>分钟`)
        )
    }
    $("#essay").append(markdown(true).render(data[2].replace(/(---[\s\S]*?---)/,"")))
    data[4].reverse().forEach((value,index)=>makeComment(value).appendTo($("#comments")))
    createToc(document)
    pangu.autoSpacingPage()
    setTimeout(()=>{
        $("body").fadeIn(1000)
        $(".list").fadeIn()
        if (window.location.href.indexOf("#")<0) {
            $(window).scrollTop(parseFloat(localStorage.getItem("scroll")))
        }
        $(window).on("scroll",function () {
            localStorage.setItem("scroll",$(this).scrollTop())
        })
    },800)
})