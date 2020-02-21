<template>
    <v-form v-model="valid">
        <v-container>
            <v-row>
                <v-col cols="12" lg="12" class="pt-0 pb-0">
                    <v-text-field single-line
                                  label="Search"
                                  v-model="searchValue"
                                  append-icon="search"
                                  v-on:keyup.enter="search"
                    />
                </v-col>
            </v-row>

            <v-row justify="end">
                <v-col cols="12" lg="4" class="pt-0 pb-0">
                    <v-select ref="levels"
                              v-model="selectedLevels"
                              :items="allLevels"
                              label="Levels"
                              multiple>
                    </v-select>
                </v-col>

                <v-col cols="12" lg="4" class="pt-0 pb-0">
                    <v-select ref="modules"
                              v-model="selectedModules"
                              :items="allModules"
                              label="Modules"
                              multiple>
                        <template v-slot:prepend-item>
                            <v-list-item ripple @click="modulesToggle">
                                <v-list-item-action>
                                    <v-icon :color="selectedModules.length > 0 ? 'indigo darken-4' : ''">
                                        {{ modulesToggleIcon }}
                                    </v-icon>
                                </v-list-item-action>
                                <v-list-item-content>
                                    <v-list-item-title>Select All</v-list-item-title>
                                </v-list-item-content>
                            </v-list-item>
                            <v-divider class="mt-2"></v-divider>
                        </template>
                        <template v-slot:selection="{ item, index }">
                            <div v-if="index == 0" class="v-select__selection v-select__selection--comma">
                                {{ item }}
                            </div>
                            <div v-if="index == 0" class="grey--text caption">
                                (+{{ selectedModules.length - 1 }} others)
                            </div>
                        </template>
                    </v-select>
                </v-col>

                <v-col cols="12" lg="4" class="pt-0 pb-0">
                    <v-menu ref="menu"
                            v-model="datePickerMenu"
                            :close-on-content-click="false"
                            :return-value.sync="period"
                            transition="scale-transition"
                            offset-y
                            full-width
                            min-width="290px">
                        <template v-slot:activator="{ on }">
                            <v-text-field v-model="periodText"
                                          label="Date range"
                                          prepend-icon="event"
                                          readonly
                                          v-on="on"/>

                        </template>
                        <v-date-picker v-model="period" range no-title scrollable>
                            <v-spacer/>
                            <v-btn text color="primary" @click="datePickerMenu = false">Cancel</v-btn>
                            <v-btn text color="primary" @click="$refs.menu.save(period)">OK</v-btn>
                        </v-date-picker>
                    </v-menu>
                </v-col>
            </v-row>
        </v-container>
    </v-form>
</template>

<script>
    export default {
        name: "SearchForm",
        data() {
            return {
                valid: false,
                datePickerMenu: false,
                loading: false,
                searchValue: "",
                searchRule: [],
                selectedLevels: ['ERROR', 'WARN', 'INFO', 'DEBUG'],
                allLevels: ['ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE'],
                selectedModules: [],
                allModules: [],
                period: this.defaultPeriod(),
            }
        },
        computed: {
            periodText() {
                return this.period.join(' ~ ')
            },
            modulesToggleIcon() {
                if (this.selectedModules.length === this.allModules.length)
                    return 'mdi-close-box';
                if (this.selectedModules.length > 0)
                    return 'mdi-minus-box';
                return 'mdi-checkbox-blank-outline'
            },

        },
        mounted() {
            this.retrieveModules();
            this.search();
        },
        methods: {
            defaultPeriod() {
                return [new Date().toISOString().substr(0, 10)]
            },
            retrieveModules() {
                let that = this;
                fetch('api/modules')
                    .then(response => {
                        return response.json()
                    })
                    .then(it => {
                        that.allModules = it;
                        that.selectedModules = it;
                    });
            },
            modulesToggle() {
                this.$nextTick(() => {
                    if (this.selectedModules.length === this.allModules.length) {
                        this.selectedModules = []
                    } else {
                        this.selectedModules = this.allModules.slice()
                    }
                })
            },
            search() {
                let that = this;
                let params = {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        levels: this.selectedLevels,
                        datetime: this.period,
                        modules: this.selectedModules,
                        query: this.searchValue,
                    })
                };
                that.store.changeLoading(true);
                fetch('api/search', params)
                    .then(response => {
                        return response.json();
                    })
                    .then(it => {
                        that.store.updateEvents(it);
                    })
                    .finally(() => {
                        that.store.changeLoading(false);
                    })
            }
        }

    }
    ;
</script>
