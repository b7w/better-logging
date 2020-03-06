<template>
    <v-app>
        <v-app-bar app color="primary" dark>
            <div class="d-flex align-center">
                <v-img
                    alt="Vuetify Logo"
                    class="shrink mr-2"
                    contain
                    src="https://cdn.vuetifyjs.com/images/logos/vuetify-logo-dark.png"
                    transition="scale-transition"
                    width="40"
                />

            </div>

            <v-toolbar-title>Better Logging</v-toolbar-title>
            <v-progress-circular v-show="loading"
                                 :indeterminate="loading"
                                 :rotate="true"
                                 :size="36"
                                 :width="4"
                                 class="ml-4"/>
            <v-spacer/>
        </v-app-bar>

        <v-content>
            <v-row justify="space-around">
                <v-col cols="10">
                    <router-view/>
                </v-col>
            </v-row>
        </v-content>
    </v-app>
</template>

<script>
    export default {
        name: "App",
        data() {
            return {
                loading: false,
            }
        },
        mounted() {
            this.store.listenLoading((data) => {
                this.loading = data;
            });
        }
    }

</script>
