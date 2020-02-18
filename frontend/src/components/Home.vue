<template>
    <div>
        <SearchForm/>
        <Table/>
    </div>
</template>

<script>
    import SearchForm from "./SearchForm";
    import Table from "./Table";

    export default {
        name: "Home",

        components: {
            SearchForm,
            Table
        },

        data: () => ({
            //
        })
    };

</script>
