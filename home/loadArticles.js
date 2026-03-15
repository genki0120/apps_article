async function loadArticles(){

const sitemap = await fetch("/sitemap.xml")

const xmlText = await sitemap.text()

const parser = new DOMParser()

const xml = parser.parseFromString(xmlText,"text/xml")

const urls = [...xml.querySelectorAll("url loc")]
.map(el => el.textContent)
.filter(url => url.includes("/AppsArticle/"))

.sort((a,b)=>{

const da = a.match(/\d{8}/)?.[0] || 0
const db = b.match(/\d{8}/)?.[0] || 0

return db - da

})

const latestContainer = document.getElementById("latest-list")
const allContainer = document.getElementById("article-list")

const promises = urls.map(async url=>{

try{

const res = await fetch(url)

const html = await res.text()

const doc = new DOMParser().parseFromString(html,"text/html")

const title = doc.querySelector("title")?.innerText || ""

const desc = doc.querySelector('meta[name="description"]')?.content || ""

const og = doc.querySelector('meta[property="og:image"]')?.content || ""

const date = url.match(/\d{8}/)?.[0] || ""

return {title,desc,og,date,url}

}catch(e){

return null

}

})

const articles = (await Promise.all(promises)).filter(Boolean)

articles.forEach((article,index)=>{

const card = document.createElement("a")

card.href = article.url
card.className = "card"

card.innerHTML = `

<img src="${article.og}" loading="lazy" width="320" height="180">

<div class="card-body">

<div class="card-title">${article.title}</div>

<div class="card-desc">${article.desc}</div>

<div class="card-date">${article.date}</div>

</div>

`

allContainer.appendChild(card)

if(index < 6){

latestContainer.appendChild(card.cloneNode(true))

}

})

generateStructuredData(articles)

}

function generateStructuredData(articles){

const list = {

"@context":"https://schema.org",
"@type":"ItemList",
"itemListElement":articles.slice(0,20).map((a,i)=>({

"@type":"ListItem",
"position":i+1,
"url":a.url,
"name":a.title

}))

}

const script = document.createElement("script")

script.type="application/ld+json"

script.textContent = JSON.stringify(list)

document.head.appendChild(script)

}

loadArticles()