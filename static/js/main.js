const createScribForm = document.querySelector('.scrib-form');
const formDiv = document.querySelector('.form-div');
const loadingGif = document.querySelector('.loading');
const scribsList = document.querySelector('.scribs-list');
const scribsFilterInput = document.querySelector('#scribs-filter-search');
const allScribsBtn = document.querySelector("#all-btn")
const myScribsBtn = document.querySelector("#mine-btn")
const loggedInUser = document.querySelector("#logged-in-user")?.textContent;

const baseAPIurl = "https://scribcraft-flask.herokuapp.com";

let scribs_list = [];

// form submit loading
const toggle = (elem) => {
    elem.classList.toggle('is-visible');
};

createScribForm?.addEventListener('submit', () => {
    toggle(formDiv);
    toggle(loadingGif);
});

// Filter scribs
scribsFilterInput?.addEventListener('input', async (e) => {
    scribsList.innerHTML = "";
    const searchValue = e.currentTarget.value.toLowerCase();
    if (scribs_list.length === 0) {
        scribs = await getScribs();
        scribs_list = [...scribs.scribs];
        console.log(scribs_list)
    }
    const filtered_list = scribs_list.filter((scrib) => scrib.title.toLowerCase().includes(searchValue)).forEach(scrib => {
        addScribToDom(createScribCardTemplate(scrib))
    })
})

allScribsBtn?.addEventListener('click', async (e) => {
    scribsList.innerHTML = "";
    if (scribs_list.length === 0) {
        scribs = await getScribs();
        scribs_list = [...scribs.scribs];
    }
    scribs_list.forEach(scrib => {
        addScribToDom(createScribCardTemplate(scrib))
    })
})

myScribsBtn?.addEventListener('click', async (e) => {
    scribsList.innerHTML = "";
    if (scribs_list.length === 0) {
        scribs = await getScribs();
        scribs_list = [...scribs.scribs];
    }
    scribs_list.filter(scrib => scrib.user_username === loggedInUser).forEach(scrib => {
        addScribToDom(createScribCardTemplate(scrib))
    })
})

const getScribs = async () => {
    const res = await axios.get(`${baseAPIurl}/api/scribs`)
    console.log("api call")
    return res.data;
};

const addScribToDom = (scrib_dom_template) => {
    scribsList.insertAdjacentHTML("beforeend",scrib_dom_template)
}

// creates template for a scrib in scrib list 
const createScribCardTemplate = (scrib) => {
    return `
        <a href="/scribs/${scrib.id}">
            <h4>${scrib.title}</h4>
            <p class="scrib-date"><strong>Created:</strong> ${scrib.timestamp}</p>
            <div class="lower-half">
            <ul>
                <li>
                    <div class="avatar">
                        <img src="${scrib.user_image_url}" alt="user's avatar">
                    </div>
                </li>
            </ul>
            </div>
        </a>
</div>`
}
