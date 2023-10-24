// Themes
export const lightMode = {
  body_bg: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
  msger_bg: '#fff',
  border: '1px solid #ddd',
  left_msg_bg: '#ececec',
  left_msg_txt: 'black',
  right_msg_bg: 'rgb(140, 0, 255)',
  msg_header_bg: 'rgba(238,238,238,0.75)',
  msg_header_txt: '#666',
  clear_btn_txt: '#999',
  msg_chat_bg_scrollbar: '#ddd',
  msg_chat_bg_thumb: '#bdbdbd',
  msg_chat_bg: '#fcfcfe',
  msg_input_bg: '#ddd',
  msg_input_area_bg: '#eee',
  msg_invert_image: 'invert(0%)',
  msg_input_color: "black",
  right_msg_txt: 'white',
  // legacy, not used
  imessageInterface_: {
    display_images: 'block',
    border_radius_all: '15px',
    msg_bubble_max_width: '450px',
    msg_bubble_width: 'unset',
    msg_margin: '5px',
    msg_chat_padding: '10px',
    right_msg_txt: 'white',
    msg_padding: '0',
    right_msg_bg_bgd: 'transparent',
  },
  // this is the interface
  normalInterface_: {
    display_images: 'none',
    border_radius_all: '0px',
    msg_bubble_max_width: 'unset',
    msg_bubble_width: '100%',
    msg_margin: '0',
    msg_chat_padding: '0',
    msg_chat_bg: '#f1f1f1',
    right_msg_bg: 'white',
    right_msg_txt: 'black',
    left_msg_bg: 'transparent',
    msg_padding: '5px 20px',
    right_msg_bg_bgd: 'white',
  }

}

export function JSONparse(exp, or='') {
    try {
        let a = JSON.parse(exp)
        return a;
    } catch (e) {
        return or;
    }
}

export const darkMode = {
  body_bg: 'linear-gradient(135deg, #3e3c46 0%, #17232c 100%)',
  msger_bg: '#2d2d2d',
  border: '1px solid #2d2d2d',

  left_msg_txt: 'white',
  right_msg_bg: 'rgb(140, 0, 255)',
  msg_header_bg: 'rgba(41,41,41,0.75)',
  msg_header_txt: '#d5d5d5',
  clear_btn_txt: '#e5e5e5',
  msg_chat_bg_scrollbar: 'transparent',
  msg_chat_bg_thumb: '#656172',
  msg_input_bg: '#2f2f2f',
  msg_input_area_bg: '#252525',
  msg_invert_image: 'invert(100%)',
  msg_input_color: "white",
  right_msg_txt: 'white',
  msg_chat_bg: '#3e3c46',
  // legacy, not used
  imessageInterface_: {
    display_images: 'block',
    border_radius_all: '15px',
    msg_bubble_max_width: '450px',
    msg_bubble_width: 'unset',
    msg_margin: '5px',
    msg_chat_padding: '10px',
    right_msg_txt: 'white',
    right_msg_bg: 'rgb(140, 0, 255)',
    msg_header_bg: 'rgba(48,48,59,0.75)',
    msg_input_area_bg: '#3e3c46',
    msg_input_bg: '#2e2e33',
    left_msg_bg: '#302f36',
    msg_padding: '0',
    right_msg_bg_bgd: 'transparent',
  },
  // this is the interface
  normalInterface_: {
    msg_chat_bg_scrollbar: '#52505b',
    display_images: 'none',
    border_radius_all: '10px',
    msg_bubble_max_width: 'unset',
    msg_bubble_width: '100%',
    msg_margin: '0',
    msg_chat_padding: '0',
    right_msg_bg: '#302f36',
    right_msg_txt: 'white',
    msg_header_bg: 'rgba(48,48,59,0.75)',
    msg_input_area_bg: '#3e3c46',
    left_msg_bg: 'transparent',
    msg_input_bg: '#2e2e33',
    msg_padding: '5px 20px',
    right_msg_bg_bgd: '#302f36',
  }
}

export function setProperties() {
    const theme = localStorage.getItem('theme')
    const interfaceTheme = 'normal'
  const object = theme === 'dark' ? darkMode : lightMode
  const interfaceObject = interfaceTheme === 'normal' ? object.normalInterface_ : object.imessageInterface_
  setPropertiesHelper(object)
  setPropertiesHelper(interfaceObject)
}
function setPropertiesHelper(themeObject) {

  for (let key in themeObject) {
    if(key.endsWith('_')) {

    } else {
      const property_replaced = key.replace(/_/g, '-')
      const property_name = `--${property_replaced}`
      const value = themeObject[key]

      document.documentElement.style.setProperty(property_name, value)
    }
  }
}

document.querySelectorAll(".no-enter").forEach(el=>{
  el.addEventListener("keypress", function(event){
    if (event.which == '13') {
      event.preventDefault();
    }
})
})