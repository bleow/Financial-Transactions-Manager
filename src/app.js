import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import VueAwesomePaginate from "vue-awesome-paginate";
// import {Amplify, Storage} from 'aws-amplify';

// Amplify.configure({
//     Auth: {
//         identityPoolId: process.env.VUE_APP_IDENTITYPOOLID,
//         region: process.env.VUE_APP_REGION
//     },
//     Storage: {
//         AWSS3: {
//             bucket: process.env.VUE_APP_BUCKETNAME,
//             region: process.env.VUE_APP_BUCKETREGION
//         }
//     }
// });

const app = createApp(App);
// app.config.globalProperties.userID = "b2e42eae-b83a-42dc-952c-5ea71cc5f0d9";
app.use(router);
app.use(VueAwesomePaginate);
app.mount("#app");
