const inner = document.querySelector(".inner-contents");
const text = inner?.innerText ?? "";

const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
const a = document.createElement("a");
a.href = URL.createObjectURL(blob);
a.download = "article.txt";
a.click();
URL.revokeObjectURL(a.href);


// xbanxia
const inner2 = document.querySelector("#nr1");
const text2 = inner2?.innerText ?? "";

const blob2 = new Blob([text2], { type: "text/plain;charset=utf-8" });
const a = document.createElement("a");
a.href = URL.createObjectURL(blob2);
a.download = "article.txt";
a.click();
URL.revokeObjectURL(a.href);
