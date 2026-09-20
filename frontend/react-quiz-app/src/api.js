//file to call the backend api using the env variable for the url path
//the function will handle the fetching so all we need to do in components is just call the function with the path we want from backend and any body info
const BASE = import.meta.env.VITE_API_URL; //searches the env file to grab the url var
export async function fetchApi(path, options={}){
    const response = await fetch(`${BASE}${path}`, {
        credentials: "include",
        ...options
        });
    if(!response.ok){
        const body = await response.json().catch(() => ({}));//get error in body
        throw new Error(body.detail || response.statusText);
    }
    return response.json();//this is the success case
}