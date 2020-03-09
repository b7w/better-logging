<template>
    <v-container fluid>
        <p class="caption text--secondary ml-4">Found {{ count }} events</p>

        <v-data-table :headers="headers"
                      :items="[]"
                      :disable-pagination="true"
                      :disable-sort="true"
                      :hide-default-footer="true"
                      :dense="true"
                      class="event-table elevation-1"
                      item-key="id">
        </v-data-table>

    </v-container>
</template>

<style>
    .event-table td.text-start {
        vertical-align: text-top;
        border-bottom-style: dashed !important;
    }
</style>

<script>
    export default {
        data() {
            return {
                headers: [
                    {text: 'App', value: 'app', width: 64},
                    {text: 'Datetime', value: 'datetime', width: 200},
                    {text: 'Level', value: 'level', width: 48},
                    {text: 'Logger', value: 'logger_name', width: 48},
                    {text: 'Trace', value: 'trace_id', width: 300},
                    {text: 'Message', value: 'message'},
                ],
                count: 0,
            }
        },
        methods: {
            createTr: function (event) {
                let el = document.createElement("tr");
                el.appendChild(this.createTd(event.app));
                el.appendChild(this.createTd(event.datetime));
                el.appendChild(this.createTd(event.level));
                el.appendChild(this.createTd(event.logger_name));
                el.appendChild(this.createTd(event.trace_id));
                el.appendChild(this.createTd(event.message));
                return el
            },
            createTd: function (value) {
                let el = document.createElement("td");
                el.setAttribute("class", "text-start");
                el.appendChild(document.createTextNode(value));
                return el
            },
        },
        mounted() {
            let events = document.querySelector('.event-table tbody');

            this.store.listenClearEvents(() => {
                events.innerHTML = '';
                this.count = 0;
            });
            this.store.listenAppendEvents((data) => {
                if (Array.isArray(data)) {
                    this.count += data.length;
                    for (let event of data) {
                        events.appendChild(this.createTr(event))
                    }
                } else {
                    this.count += 1;
                    events.appendChild(this.createTr(data))
                }
            });
        },
    }
</script>
