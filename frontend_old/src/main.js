import './app.css'
import App from './App.svelte'

const app = new App({
  target: document.getElementById('app'), // Make sure this matches your HTML
  props: {
    name: 'Yanga Yanga'
  }
})

export default app
