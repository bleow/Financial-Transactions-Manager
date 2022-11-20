<script setup>
defineProps({
    title: {
        type: String,
        required: false
    },
    success:{
        type:Boolean,
        required: false
    },
    fail:{
        type:Boolean,
        required: false
    },
    error:{
        type:String,
        required:false
    }
})
</script>

<script>
export default {
    data() {
        return{
            show:true
        }
    },
    methods: {
      close(){
        this.show=false;
        this.$emit('close', "close");
      }
    }
};
</script>

<template>
    <div v-show="show" class="row successRow d-flex align-items-center justify-content-center">
        <div v-if="success" class="col-12 text-center">
            <img class="img-fluid mx-auto d-block"  src="../assets/tick.png"/>
            <br>
            <h6 class="text-capitalize text-center">{{title}} Success</h6>
        </div>

        <div v-if="fail" class="col-12 text-center">
            <img class="img-fluid mx-auto d-block"  src="../assets/exclamation-mark.png"/>
            <br>
            <h6 class="text-capitalize text-center">{{error}}</h6>
        </div>

      <button type="button" @click="close" class="btn btn-primary w-50">OK</button>
    </div>
    <br>
</template>

<style scoped>
.successRow{
    padding-top:30px
}

@media only screen and (min-width: 1000px) {
  img {
    width:20%;
    height:60%
  }
}
</style>