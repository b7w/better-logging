<template>
    <v-container fluid>
        <p class="caption text--secondary ml-4">Found {{ count }} events</p>

        <div class="v-data-table event-table elevation-1 v-data-table--dense theme--light">
            <div class="v-data-table__wrapper">
                <table>
                    <colgroup>
                        <col class="">
                        <col class="">
                        <col class="">
                        <col class="">
                        <col class="">
                    </colgroup>
                    <thead class="v-data-table-header">
                    <tr>
                        <th role="columnheader" scope="col" aria-label="App" aria-sort="none" class="text-start"
                            style="width: 64px; min-width: 64px;">
                            <span>App</span>
                        </th>
                        <th role="columnheader" scope="col" aria-label="Datetime" aria-sort="none" class="text-start"
                            style="width: 196px; min-width: 196px;">
                            <span>Datetime</span>
                        </th>
                        <th role="columnheader" scope="col" aria-label="Level" aria-sort="none" class="text-start"
                            style="width: 48px; min-width: 48px;">
                            <span>Level</span>
                        </th>
                        <th role="columnheader" scope="col" aria-label="Logger" aria-sort="none" class="text-start"
                            style="width: 32px; min-width: 32px;">
                            <span>Logger</span>
                        </th>
                        <th role="columnheader" scope="col" aria-label="Message" aria-sort="none" class="text-start">
                            <span>Message</span>
                        </th>
                    </tr>
                    </thead>
                    <tbody id="events"></tbody>
                </table>
            </div>
        </div>

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
                    {text: 'Datetime', value: 'datetime', width: 196},
                    {text: 'Level', value: 'level', width: 48},
                    {text: 'Logger', value: 'logger_name', width: 32},
                    {text: 'Message', value: 'message'},
                    {text: '', value: 'data-table-expand', width: 32},
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
            let events = document.getElementById("events");

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
