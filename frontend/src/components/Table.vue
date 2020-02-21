<template>
    <v-container>
        <p class="caption text--secondary ml-4">Found {{ eventsCount }} events</p>

        <v-data-table :headers="headers"
                      :items="events"
                      :loading="loading"
                      :loading-text="'Loading... Please wait'"
                      :disable-pagination="true"
                      :disable-sort="true"
                      :hide-default-footer="true"
                      :dense="true"
                      :single-expand="true"
                      class="elevation-1"
                      item-key="id"
                      show-expand>
            <template v-slot:expanded-item="{ headers }">
                <td :colspan="headers.length">Peek-a-boo!</td>
            </template>
        </v-data-table>

    </v-container>
</template>

<style>
    td {
        word-wrap: break-word;
        white-space: pre-line;
        overflow-wrap: break-word;
    }
</style>

<script>
    export default {
        data() {
            return {
                headers: [
                    {text: 'App', value: 'app', width: 64},
                    {text: 'Datetime', value: 'datetime', width: 196},
                    {text: 'Level', value: 'level', width: 48},
                    {text: 'Logger', value: 'logger_name', width: 48},
                    {text: 'Message', value: 'message', width: 196},
                    {text: '', value: 'data-table-expand', width: 32},
                ],
                loading: false,
                events: [],
            }
        },
        mounted() {
            this.store.listenUpdateEvents((data) => {
                this.events = data;
            });
            this.store.listenLoading((data) => {
                this.loading = data;
            });
        },
        computed: {
            eventsCount() {
                return this.events.length
            },
        },
    }
</script>
