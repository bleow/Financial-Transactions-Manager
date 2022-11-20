<script setup>
import SuccessTransaction from "../components/SuccessTransaction.vue";
// import { Storage } from 'aws-amplify';
</script>


<script>
export default {
  data() {
    var filelist = [];
    return { 
      filetype: ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,', 'application/vnd.ms-excel'],
      filelist: [],
      showSuccess: false,
      showFile: true,
      showError: false,
      errorMsg: ''
    } 
  },
  methods: {
    // default is to open file in new window
    onDragover(event) {
      event.preventDefault();
    },
    onDrop(event) {
      event.preventDefault();
      // access the DOM
      this.$refs.file.files = event.dataTransfer.files;
      this.onChange();
    },
    onChange() {
      // spread operator
      this.filelist = [...this.$refs.file.files];
    },
    onBrowse(){
      const elem = this.$refs.file;
      elem.click();
    },
    onUpload(){
      if (this.filelist.length == 0){
        this.showError = true;
        this.showFile = false;
        this.errorMsg = 'Please select a file to upload'
      } else if(this.filetype.includes(this.filelist[0].type) == false){
        this.showError = true;
        this.showFile = false;
        this.errorMsg = 'Unsupported File Type'
      } else {
        Storage.put(this.filelist[0].name, this.filelist[0], {})
            .then((data) => {
              this.showFile = false;
              this.showSuccess=true;
            })
            .catch((err) => {
              this.showFile = false;
              this.showError=true;
              this.errorMsg=err;
            })
      }
    },
    onClose(value){
        this.showSuccess = false;
        this.showError = false;
        this.showFile = true;
        this.errorMsg = '';
        this.filelist = [];
      }
  },
    components:{
      SuccessTransaction
    }
}
</script>

<template>
  <main class="main-content">
    <div class="content">
      <h1>File Upload</h1>
      <br>
      <!-- Upload File -->
      <div v-if="showFile" class="row d-flex align-items-center justify-content-center">
        <div class="col-md-8">
          <div class="upload-box" v-on:dragover="onDragover" v-on:drop="onDrop">
            <input type="file" multiple name="fields[assetsFieldHandle][]" id="assetsFieldHandle" v-on:change="onChange" ref="file" accept=".csv, .xlsx"/>
              <span class="upload-icon">
                <i class="icon-cloud-upload primary font-large-2"></i>
              </span>
              <h6 class="upload-text">Drag and drop, or <span v-on:click="onBrowse">browse</span> your files</h6>
            <span v-if="filelist[0]">
              {{filelist[0].name }}
            </span>
          </div>
            <a class="col-12 btn btn-primary" v-on:click="onUpload">Upload</a>
        </div>
      </div>
      
      <div v-if="showError">
        <SuccessTransaction v-on:close="onClose" :fail=showError :error=errorMsg ></SuccessTransaction>
      </div>
      <div v-if="showSuccess">
        <SuccessTransaction v-onclose="onClose" :success=showSuccess title="file upload"></SuccessTransaction>
      </div>

    </div>
  </main>
</template>

<style>
.main-content {
  padding-top: 80px;
  padding-left: 20px;
  padding-right: 20px;
}

/* hide the Choose file popup */
#assetsFieldHandle {
  display: none;
}

.upload-box {
  text-align: center;
  border: 2px dashed #777;
  padding: 50px;
  margin-bottom: 20px;
  border-radius: 10px;
}
.upload-box span {
  display: block;
}

.upload-icon {
  font-size: 40px;
}
.upload-text span{
  display: inline;
  color: #0078ef;
  cursor: pointer;
}

.btn{
  color: white !important;
}
</style>
