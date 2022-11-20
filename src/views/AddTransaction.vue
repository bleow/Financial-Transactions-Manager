<script>
import SuccessTransaction from "../components/SuccessTransaction.vue";
import currencies from "currencies.json";
import axios from "axios";

export default {
  data() {
    let props = {
      mcc: "",
      merchant: "",
      currency: "",
      amount: "",
      cardtype: "",
      transactionDate: "",
      cardNum: "",
    };
    return {
      showSuccess: false,
      showTrans: true,
      showError: false,
      errormsge: "",
      props,
      currencyCode: [],
      transaction: {}
    };
  },
  methods: {
    async sendTransaction() {
      this.showTrans = false;
      var fieldsKeys = Object.keys(this.props);
      fieldsKeys.forEach((key) => {
        if (this.props[key] == undefined || this.props[key] == "") {
          this.errormsge = "Field Required is empty";
          this.showError = true;
        }
      });
      if (this.errormsge.length == 0) {
        var data = JSON.stringify({
          transaction_date: this.props.transactionDate,
          merchant: this.props.merchant,
          mcc: this.props.mcc,
          currency: this.props.currency,
          amount: this.props.amount,
          card_pan: this.props.cardNum,
          card_type: this.props.cardtype
        });
        console.log(data);

        var config = {
        method: 'post',
        url: 'http://127.0.0.1:8080',
          //url: 'https://wn67is82a0.execute-api.us-east-1.amazonaws.com/1/transactions',
        headers: {
        'Content-Type': 'application/json'
        },
        data : data
        };

        axios(config).then(response=>{
        if(response['data'] != "Success"){
          this.errormsge = response['data'];
          this.showError = true;
          this.showSuccess = false;
          this.showTrans = false;
        }
        else{
          this.showError = false;
          this.showSuccess = true;
          this.showTrans = false;
        }
        })
        .catch(function (error) {
        console.log(error);
        });
      }
    },
    close(value) {
      if (value == "close") {
        this.showSuccess = false;
        this.showError = false;
        this.showTrans = true;
        this.errormsge = "";

        Object.keys(this.props).forEach((key) => (this.props[key] = ""));
      }
    },
    closeError(value) {
      if (value == "close") {
        this.showSuccess = false;
        this.showError = false;
        this.showTrans = true;
        this.errormsge = "";
      }
    },
  },
  computed: {
    getCurrencyCode() {
      this.currencyCode = [];
      for (let i = 0; i < currencies.currencies.length; i++) {
        this.currencyCode.push(currencies.currencies[i]["code"]);
      }
      return this.currencyCode;
    },
  },
  components: {
    SuccessTransaction,
  },
};
</script>


<template>
  <main class="main-content">
    <div class="row">
      <div class="col-12">
        <h1>Add Transaction</h1>
        <br />
        <div v-if="showTrans">
          <div class="row">
            <div class="col-md-12 form-group">
              <label for="transactionDate">Transaction date *</label>
              <input
                type="date"
                v-model="props.transactionDate"
                class="form-control"
                name="transactionDate"
                placeholder="Username"
              />
            </div>
            <div class="col-md-6 form-group">
              <label for="merchant">Merchant *</label>
              <input
                type="text"
                v-model="props.merchant"
                class="form-control"
                name="merchant"
                placeholder="Enter Merchant"
              />
            </div>
            <div class="col-md-6 form-group">
              <label for="mcc">MCC *</label>
              <input
                type="number"
                v-model="props.mcc"
                class="form-control"
                name="mcc"
                placeholder="Enter MCC"
              />
            </div>
          </div>
          <div class="row">
            <div class="col-md-6 form-group">
              <label for="currency">Currency *</label>
              <select
                class="form-control"
                v-model="props.currency"
                id="currency"
              >
                <option v-for="code in getCurrencyCode" :value="code">
                  {{ code }}
                </option>
              </select>
            </div>
            <div class="col-md-6 form-group">
              <label for="amount">Transaction Amount *</label>
              <input
                type="number"
                v-model="props.amount"
                class="form-control"
                name="mcc"
                placeholder="Transaction Amount"
              />
            </div>
          </div>
          <div class="row">
            <div class="col-md-6 form-group">
              <label for="cardtype">Card Type</label>
              <select
                class="form-control"
                v-model="props.cardtype"
                id="cardtype"
              >
                <option value="scis_platinummiles">scis_platinummiles</option>
                <option value="scis_shopping">scis_shopping</option>
                <option value="scis_freedom">scis_freedom</option>
                <option value="scis_premiummiles">scis_premiummiles</option>
              </select>
            </div>
            <div class="col-md-6 form-group">
              <label for="cardNum">Card Pan *</label>
              <input
                type="number"
                v-model="props.cardNum"
                class="form-control"
                name="cardNum"
                placeholder="Enter Card Pan"
              />
            </div>
          </div>
          <div class="row">
            <div class="col-12 form-group">
              <button
                class="float-right btn btn-primary"
                @click="sendTransaction"
              >
                Add Transaction
              </button>
            </div>
          </div>
        </div>

        <div v-if="showError">
          <SuccessTransaction @close="closeError" :fail="showError" :error="errormsge"></SuccessTransaction>
        </div>
        <div v-if="showSuccess">
          <SuccessTransaction @close="close" :success="showSuccess" title="transaction added"></SuccessTransaction>
        </div>

      </div>
    </div>
  </main>
</template>

<style scoped>
.main-content {
  padding-top: 80px;
  padding-left: 20px;
  padding-right: 20px;
}
</style>
