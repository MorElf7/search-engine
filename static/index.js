let query = "";
const listItemClass = "py-2 font-semibold text-2xl";

const handleSubmitQuery = async (e) => {
  e.preventDefault();
  if (query !== "") {
    const response = await (await fetch(`/search?query=${query}`)).json();
    const data = response.data;
    const list = document.getElementById("results-list");
    if (data.length === 0) {
      const listItem = document.createElement("p");
      listItem.className = listItemClass;
      listItem.innerText = "Your search did not match any documents";
      list.appendChild(listItem);
    } else {
      for (let item of data) {
        const listItem = document.createElement("li");
        listItem.className = listItemClass;
        const [play, act, scene] = item.split(":");
        listItem.innerText = `${play} Act ${act} Scene ${scene}`;
        list.appendChild(listItem);
      }
    }
  }
};

const handleQueryChange = (e) => {
  e.preventDefault();
  if (e.key === "Enter") {
    handleSubmitQuery(e);
    return;
  }
  query = e.target.value;
};

document
  .getElementById("query_input")
  .addEventListener("keyup", handleQueryChange);
document
  .getElementById("query_submit")
  .addEventListener("click", handleSubmitQuery);
