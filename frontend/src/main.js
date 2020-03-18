import Vue from "vue";
import App from "./App.vue";
import VueRouter from "vue-router";
import Home from "./components/Home";
import Vuetify from "vuetify/lib";
import 'material-design-icons-iconfont/dist/material-design-icons.css';

Vue.config.productionTip = false;
Vue.config.devtools = true;
Vue.config.performance = true;


Vue.use(VueRouter);
Vue.use(Vuetify);

class EventBus {
    constructor() {
        this.store = {}
    }

    buffer_factory(cl, maxLen = 4, maxTime = 10) {
        let events = [];
        return function (data) {
            events.push(data);
            if (events.length >= maxLen) {
                console.log('Flush count ' + events.length);
                cl(events.splice(0));
            }
            setInterval(function () {
                if (events.length > 0) {
                    console.log('Flush time ' + events.length);
                    cl(events.splice(0));
                }
            }, maxTime)
        }
    }

    $on(name, callback) {
        if (!this.store[name]) {
            this.store[name] = [callback]
        } else {
            this.store[name].push(callback);
        }
    }

    $emit(name, data) {
        let callbacks = this.store[name];
        if (callbacks) {
            for (let callback of callbacks) {
                callback(data);
            }
        }
    }
}

let store = {
    eventBus: new EventBus(),
    changeLoading(data) {
        this.eventBus.$emit('change_loading', data);
    },
    listenLoading(callback) {
        return this.eventBus.$on('change_loading', callback);
    },
    clearEvents() {
        this.eventBus.$emit('clear_events');
    },
    appendEvents(data) {
        this.eventBus.$emit('append_events', data);
    },
    listenClearEvents(callback) {
        return this.eventBus.$on('clear_events', callback);
    },
    listenAppendEvents(callback) {
        return this.eventBus.$on('append_events', callback);
    }
};
Vue.prototype.store = store;


const routes = [
    {
        path: "/",
        name: "home",
        component: Home
    },
    {
        path: "/about",
        name: "about",
        component: () => import("./components/About.vue")
    }
];

const router = new VueRouter({
    routes
});

const vuetify = new Vuetify({
    icons: {
        iconfont: 'md',
    },
});

new Vue({
    router: router,
    vuetify: vuetify,
    render: h => h(App)
}).$mount("#app");
