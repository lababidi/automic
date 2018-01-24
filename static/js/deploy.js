/**
 * Created by miclark on 12/21/17.
 */

        angular.module('myApp', [])
            .controller('HomeCtrl', function($scope, $http) {

				$scope.info = {};

				$scope.showAdd = true;

				$scope.showlist = function(){
					$http({
						method: 'POST',
						url: '/getMachineList',

					}).then(function(response) {
						$scope.machines = response.data;
						console.log('mm',$scope.machines);
					}, function(error) {
						console.log(error);
					});
				}



				$scope.addMachine = function(){



					$http({
						method: 'POST',
						url: '/addMachine',
						data: {info:$scope.info}
					}).then(function(response) {
						$scope.showlist();
						$('#addPopUp').modal('hide')
						$scope.info = {}
					}, function(error) {
						console.log(error);
					});
				}

				$scope.editMachine = function(id){
					$scope.info.id = id;

					$scope.showAdd = false;

					$http({
						method: 'POST',
						url: '/getMachine',
						data: {id:$scope.info.id}
					}).then(function(response) {
						console.log(response);
						$scope.info = response.data;
						$('#addPopUp').modal('show')
					}, function(error) {
						console.log(error);
					});
				}

				$scope.updateMachine = function(id){

					$http({
						method: 'POST',
						url: '/updateMachine',
						data: {info:$scope.info}
					}).then(function(response) {
						console.log(response.data);
						$scope.showlist();
						$('#addPopUp').modal('hide')
					}, function(error) {
						console.log(error);
					});
				}


				$scope.showAddPopUp = function(){
					$scope.showAdd = true;
					$scope.info = {};
					$('#addPopUp').modal('show')
				}

				$scope.showRunPopUp = function(id){

					$scope.info.id = id;
					$scope.run = {};




					$http({
						method: 'POST',
						url: '/getMachine',
						data: {id:$scope.info.id}
					}).then(function(response) {
						console.log(response);
						$scope.run = response.data;
						$scope.run.isRoot = false;
						$('#runPopUp').modal('show');
					}, function(error) {
						console.log(error);
					});



				}

				$scope.confirmDelete = function(id){
					$scope.deleteMachineId = id;
					$('#deleteConfirm').modal('show');
				}

				$scope.deleteMachine = function(){

					$http({
						method: 'POST',
						url: '/deleteMachine',
						data: {id:$scope.deleteMachineId}
					}).then(function(response) {
						console.log(response.data);
						$scope.deleteMachineId = '';
						$scope.showlist();
						$('#deleteConfirm').modal('hide')
					}, function(error) {
						console.log(error);
					});
				}


				$scope.executeCommand = function(){


					console.log($scope.run);

					$http({
						method: 'POST',
						url: '/execute',
						data: {info:$scope.run}
					}).then(function(response) {
						console.log(response);
						$scope.run.response = response.data.message;
					}, function(error) {
						console.log(error);
					});
				}

				$scope.showlist();
            })
