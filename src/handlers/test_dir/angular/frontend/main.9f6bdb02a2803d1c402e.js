(window["webpackJsonp"] = window["webpackJsonp"] || []).push([["main"],{

/***/ "/7gl":
/*!*******************************************!*\
  !*** ./src/app/tree/ngrx/tree.reducer.ts ***!
  \*******************************************/
/*! exports provided: reducer, selectTreeState */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "reducer", function() { return reducer; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "selectTreeState", function() { return selectTreeState; });
/* harmony import */ var _tree_actions__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./tree.actions */ "Nj3k");

;
const initialState = {
    type: undefined,
    payload: undefined,
    data: undefined,
};
function reducer(state = initialState, action) {
    switch (action.type) {
        case _tree_actions__WEBPACK_IMPORTED_MODULE_0__["TreeActionTypes"].SetData:
            return Object.assign(Object.assign({}, state), { type: action.type, data: action.payload });
        case _tree_actions__WEBPACK_IMPORTED_MODULE_0__["TreeActionTypes"].ResetData:
            return Object.assign(Object.assign({}, state), { type: action.type, data: null });
        default:
            return Object.assign(Object.assign({}, state), { type: action.type, payload: action.payload });
    }
}
const selectTreeState = (rootState) => rootState.TreeState;


/***/ }),

/***/ 0:
/*!***************************!*\
  !*** multi ./src/main.ts ***!
  \***************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__(/*! M:\MyFiles\Code\Javascript\Test\test-app\src\main.ts */"zUnb");


/***/ }),

/***/ "1YIm":
/*!*********************************************!*\
  !*** ./src/app/tree/tree-node.component.ts ***!
  \*********************************************/
/*! exports provided: TreeNodeComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "TreeNodeComponent", function() { return TreeNodeComponent; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "mrSG");
/* harmony import */ var _raw_loader_tree_node_component_html__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! raw-loader!./tree-node.component.html */ "eq6X");
/* harmony import */ var _tree_node_component_scss__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./tree-node.component.scss */ "TeWD");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/core */ "fXoL");
/* harmony import */ var _ngrx_store__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @ngrx/store */ "l7P3");
/* harmony import */ var _ngrx_tree_actions__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./ngrx/tree.actions */ "Nj3k");






let TreeNodeComponent = class TreeNodeComponent {
    constructor(store, cdr) {
        this.store = store;
        this.cdr = cdr;
        this.cutomContextMenu = new _angular_core__WEBPACK_IMPORTED_MODULE_3__["EventEmitter"]();
    }
    ngOnInit() {
        this.eventsSubscription = this.statusUpdate.subscribe((status) => {
            if (status.states.has(this.node.uuid)) {
                this.node.selected = status.states.get(this.node.uuid);
            }
            else if (status.defaultState !== undefined) {
                this.node.selected = status.defaultState;
            }
        });
    }
    ngOnDestroy() {
        this.eventsSubscription.unsubscribe();
    }
    identify(index, item) {
        return item.uuid;
    }
    checkboxChange() {
        this.node.selected = !this.node.selected;
        this.store.dispatch(new _ngrx_tree_actions__WEBPACK_IMPORTED_MODULE_5__["SelectItem"]({ uuid: this.node.uuid, state: this.node.selected }));
        this.cdr.detectChanges();
    }
    onNewSelectedList(uuids) {
        if (this.node.children.length > 0) { // parent node, don't care about new state
            return;
        }
        const newState = !!uuids[this.node.uuid];
        if (this.node.selected !== newState) {
            this.node.selected = newState;
            this.cdr.detectChanges();
        }
    }
};
TreeNodeComponent.ctorParameters = () => [
    { type: _ngrx_store__WEBPACK_IMPORTED_MODULE_4__["Store"] },
    { type: _angular_core__WEBPACK_IMPORTED_MODULE_3__["ChangeDetectorRef"] }
];
TreeNodeComponent.propDecorators = {
    node: [{ type: _angular_core__WEBPACK_IMPORTED_MODULE_3__["Input"] }],
    statusUpdate: [{ type: _angular_core__WEBPACK_IMPORTED_MODULE_3__["Input"] }],
    cutomContextMenu: [{ type: _angular_core__WEBPACK_IMPORTED_MODULE_3__["Output"] }]
};
TreeNodeComponent = Object(tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"])([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_3__["Component"])({
        selector: 'tree-node',
        template: _raw_loader_tree_node_component_html__WEBPACK_IMPORTED_MODULE_1__["default"],
        styles: [_tree_node_component_scss__WEBPACK_IMPORTED_MODULE_2__["default"]]
    })
], TreeNodeComponent);



/***/ }),

/***/ "7LWo":
/*!******************************************************************************!*\
  !*** ./node_modules/raw-loader/dist/cjs.js!./src/app/xyz/xyz.component.html ***!
  \******************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = ("<p>xyz works!</p>\n");

/***/ }),

/***/ "AytR":
/*!*****************************************!*\
  !*** ./src/environments/environment.ts ***!
  \*****************************************/
/*! exports provided: environment */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "environment", function() { return environment; });
// This file can be replaced during build by using the `fileReplacements` array.
// `ng build --prod` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.
const environment = {
    production: false
};
/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/dist/zone-error';  // Included with Angular CLI.


/***/ }),

/***/ "Nj3k":
/*!*******************************************!*\
  !*** ./src/app/tree/ngrx/tree.actions.ts ***!
  \*******************************************/
/*! exports provided: PayloadAction, TreeActionTypes, SetData, ResetData, SetAllSelected, SelectItem, GetHTTPAttempted, GetHTTPSuccessful */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "PayloadAction", function() { return PayloadAction; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "TreeActionTypes", function() { return TreeActionTypes; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "SetData", function() { return SetData; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "ResetData", function() { return ResetData; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "SetAllSelected", function() { return SetAllSelected; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "SelectItem", function() { return SelectItem; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "GetHTTPAttempted", function() { return GetHTTPAttempted; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "GetHTTPSuccessful", function() { return GetHTTPSuccessful; });
class PayloadAction {
    constructor(payload) {
        this.payload = payload;
    }
}
var TreeActionTypes;
(function (TreeActionTypes) {
    TreeActionTypes["SetData"] = "[TreeActionTypes] SetData";
    TreeActionTypes["ResetData"] = "[TreeActionTypes] ResetData";
    TreeActionTypes["SetAllSelected"] = "[TreeActionTypes] SetAllSelected";
    TreeActionTypes["SelectItem"] = "[TreeActionTypes] SelectItem";
    TreeActionTypes["GetHTTPAttempted"] = "[TreeActionTypes] GetHTTPAttempted";
    TreeActionTypes["GetHTTPSuccessful"] = "[TreeActionTypes] GetHTTPSuccessful";
})(TreeActionTypes || (TreeActionTypes = {}));
class SetData extends PayloadAction {
    constructor() {
        super(...arguments);
        this.type = TreeActionTypes.SetData;
    }
}
class ResetData extends PayloadAction {
    constructor() {
        super(...arguments);
        this.type = TreeActionTypes.ResetData;
    }
}
class SetAllSelected extends PayloadAction {
    constructor() {
        super(...arguments);
        this.type = TreeActionTypes.SetAllSelected;
    }
}
class SelectItem extends PayloadAction {
    constructor() {
        super(...arguments);
        this.type = TreeActionTypes.SelectItem;
    }
}
class GetHTTPAttempted extends PayloadAction {
    constructor() {
        super(...arguments);
        this.type = TreeActionTypes.GetHTTPAttempted;
    }
}
class GetHTTPSuccessful extends PayloadAction {
    constructor() {
        super(...arguments);
        this.type = TreeActionTypes.GetHTTPSuccessful;
    }
}


/***/ }),

/***/ "Sy1n":
/*!**********************************!*\
  !*** ./src/app/app.component.ts ***!
  \**********************************/
/*! exports provided: AppComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "AppComponent", function() { return AppComponent; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "mrSG");
/* harmony import */ var _raw_loader_app_component_html__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! raw-loader!./app.component.html */ "VzVu");
/* harmony import */ var _app_component_scss__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./app.component.scss */ "ynWL");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/core */ "fXoL");




let AppComponent = class AppComponent {
    constructor() {
        this.title = 'test-app';
        this.showcards = false;
        this.comp = 2;
    }
    onClickCard(event, cardnum) {
        this.comp = cardnum;
        this.showcards = false;
    }
    goBackToCards(event) {
        this.comp = -1;
        this.showcards = true;
    }
};
AppComponent = Object(tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"])([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_3__["Component"])({
        selector: 'app-root',
        template: _raw_loader_app_component_html__WEBPACK_IMPORTED_MODULE_1__["default"],
        styles: [_app_component_scss__WEBPACK_IMPORTED_MODULE_2__["default"]]
    })
], AppComponent);



/***/ }),

/***/ "TeWD":
/*!***********************************************!*\
  !*** ./src/app/tree/tree-node.component.scss ***!
  \***********************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = (".caret {\n  width: 0;\n  height: 0;\n  display: table-cell;\n  border: 6px solid transparent;\n  border-top: 9px solid transparent;\n}\n\n.caret.down {\n  border-top-color: black;\n}\n\n.caret.right {\n  border-left-color: black;\n}");

/***/ }),

/***/ "U2VC":
/*!********************************************!*\
  !*** ./src/app/tree/ngrx/tree.services.ts ***!
  \********************************************/
/*! exports provided: TreeService */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "TreeService", function() { return TreeService; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "mrSG");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "fXoL");
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/common/http */ "IheW");



const API = 'api/';
const GET_ALL = API + 'tree/2/3';
let TreeService = class TreeService {
    constructor(http) {
        this.http = http;
    }
    getAll(postData) {
        // return this.http.get(GET_ALL);
        // return this.http.post(GET_ALL, postData);
        return this.http.post(postData.api, postData.data);
    }
};
TreeService.ctorParameters = () => [
    { type: _angular_common_http__WEBPACK_IMPORTED_MODULE_2__["HttpClient"] }
];
TreeService = Object(tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"])([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Injectable"])({
        providedIn: 'root'
    })
], TreeService);



/***/ }),

/***/ "VzVu":
/*!**************************************************************************!*\
  !*** ./node_modules/raw-loader/dist/cjs.js!./src/app/app.component.html ***!
  \**************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = ("<!-- Toolbar -->\n<div class=\"toolbar\" role=\"banner\">\n  <img\n    width=\"40\"\n    alt=\"Angular Logo\"\n    src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNTAgMjUwIj4KICAgIDxwYXRoIGZpbGw9IiNERDAwMzEiIGQ9Ik0xMjUgMzBMMzEuOSA2My4ybDE0LjIgMTIzLjFMMTI1IDIzMGw3OC45LTQzLjcgMTQuMi0xMjMuMXoiIC8+CiAgICA8cGF0aCBmaWxsPSIjQzMwMDJGIiBkPSJNMTI1IDMwdjIyLjItLjFWMjMwbDc4LjktNDMuNyAxNC4yLTEyMy4xTDEyNSAzMHoiIC8+CiAgICA8cGF0aCAgZmlsbD0iI0ZGRkZGRiIgZD0iTTEyNSA1Mi4xTDY2LjggMTgyLjZoMjEuN2wxMS43LTI5LjJoNDkuNGwxMS43IDI5LjJIMTgzTDEyNSA1Mi4xem0xNyA4My4zaC0zNGwxNy00MC45IDE3IDQwLjl6IiAvPgogIDwvc3ZnPg==\"\n  />\n  <span>Welcome</span>\n    <div class=\"spacer\"></div>\n    <a aria-label=\"Angular on twitter\" target=\"_blank\" rel=\"noopener\" href=\"\" title=\"Twitter\">\n      <svg id=\"twitter-logo\" height=\"24\" data-name=\"Logo\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 400 400\">\n        <rect width=\"400\" height=\"400\" fill=\"none\"/>\n        <path d=\"M153.62,301.59c94.34,0,145.94-78.16,145.94-145.94,0-2.22,0-4.43-.15-6.63A104.36,104.36,0,0,0,325,122.47a102.38,102.38,0,0,1-29.46,8.07,51.47,51.47,0,0,0,22.55-28.37,102.79,102.79,0,0,1-32.57,12.45,51.34,51.34,0,0,0-87.41,46.78A145.62,145.62,0,0,1,92.4,107.81a51.33,51.33,0,0,0,15.88,68.47A50.91,50.91,0,0,1,85,169.86c0,.21,0,.43,0,.65a51.31,51.31,0,0,0,41.15,50.28,51.21,51.21,0,0,1-23.16.88,51.35,51.35,0,0,0,47.92,35.62,102.92,102.92,0,0,1-63.7,22A104.41,104.41,0,0,1,75,278.55a145.21,145.21,0,0,0,78.62,23\" fill=\"#fff\"/>\n      </svg>\n    </a>\n</div>\n\n<div class=\"content\" role=\"main\">\n\n  <!-- Highlight Card -->\n  <div class=\"card highlight-card card-small\">\n\n    <svg id=\"rocket\" alt=\"Rocket Ship\" xmlns=\"http://www.w3.org/2000/svg\" width=\"101.678\" height=\"101.678\" viewBox=\"0 0 101.678 101.678\">\n      <g id=\"Group_83\" data-name=\"Group 83\" transform=\"translate(-141 -696)\">\n        <circle id=\"Ellipse_8\" data-name=\"Ellipse 8\" cx=\"50.839\" cy=\"50.839\" r=\"50.839\" transform=\"translate(141 696)\" fill=\"#dd0031\"/>\n        <g id=\"Group_47\" data-name=\"Group 47\" transform=\"translate(165.185 720.185)\">\n          <path id=\"Path_33\" data-name=\"Path 33\" d=\"M3.4,42.615a3.084,3.084,0,0,0,3.553,3.553,21.419,21.419,0,0,0,12.215-6.107L9.511,30.4A21.419,21.419,0,0,0,3.4,42.615Z\" transform=\"translate(0.371 3.363)\" fill=\"#fff\"/>\n          <path id=\"Path_34\" data-name=\"Path 34\" d=\"M53.3,3.221A3.09,3.09,0,0,0,50.081,0,48.227,48.227,0,0,0,18.322,13.437c-6-1.666-14.991-1.221-18.322,7.218A33.892,33.892,0,0,1,9.439,25.1l-.333.666a3.013,3.013,0,0,0,.555,3.553L23.985,43.641a2.9,2.9,0,0,0,3.553.555l.666-.333A33.892,33.892,0,0,1,32.647,53.3c8.55-3.664,8.884-12.326,7.218-18.322A48.227,48.227,0,0,0,53.3,3.221ZM34.424,9.772a6.439,6.439,0,1,1,9.106,9.106,6.368,6.368,0,0,1-9.106,0A6.467,6.467,0,0,1,34.424,9.772Z\" transform=\"translate(0 0.005)\" fill=\"#fff\"/>\n        </g>\n      </g>\n    </svg>\n\n    <span>Running?</span>\n\n    <svg id=\"rocket-smoke\" alt=\"Rocket Ship Smoke\" xmlns=\"http://www.w3.org/2000/svg\" width=\"516.119\" height=\"1083.632\" viewBox=\"0 0 516.119 1083.632\">\n      <path id=\"Path_40\" data-name=\"Path 40\" d=\"M644.6,141S143.02,215.537,147.049,870.207s342.774,201.755,342.774,201.755S404.659,847.213,388.815,762.2c-27.116-145.51-11.551-384.124,271.9-609.1C671.15,139.365,644.6,141,644.6,141Z\" transform=\"translate(-147.025 -140.939)\" fill=\"#f5f5f5\"/>\n    </svg>\n\n  </div>\n\n  <!-- Resources -->\n  <h2>Clicks</h2>\n\n  <div class=\"card-container\" *ngIf=\"!!this.showcards\">\n    <a class=\"card\" (click)=\"onClickCard($event, 1)\">\n      <span>XYZ Comp</span>\n      <svg class=\"material-icons\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\"><path d=\"M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z\"/></svg>\n    </a>\n\n    <a class=\"card\" (click)=\"onClickCard($event, 2)\">\n      <span>Tree Comp</span>\n      <svg class=\"material-icons\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\"><path d=\"M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z\"/></svg>\n    </a>\n\n    <a class=\"card\" (click)=\"onClickCard($event, 3)\">\n      <span>Angular Blog</span>\n      <svg class=\"material-icons\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\"><path d=\"M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z\"/></svg>\n    </a>\n  </div>\n\n  <div class=\"card-container\" *ngIf=\"!this.showcards\">\n    <a class=\"card\" (click)=\"goBackToCards($event)\">\n      <span>Go Back to Menu</span>\n      <svg class=\"material-icons\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\"><path d=\"M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z\"/></svg>\n    </a>\n  </div>\n\n  <div *ngIf=\"this.comp==1\">\n    <app-xyz></app-xyz>\n  </div>\n\n  <div *ngIf=\"this.comp==2\">\n    <tree-comp></tree-comp>\n  </div>\n\n\n  <svg id=\"clouds\" alt=\"Gray Clouds Background\" width=\"2611.084\" height=\"485.677\" viewBox=\"0 0 2611.084 485.677\">\n    <path id=\"Path_39\" data-name=\"Path 39\" d=\"M2379.709,863.793c10-93-77-171-168-149-52-114-225-105-264,15-75,3-140,59-152,133-30,2.83-66.725,9.829-93.5,26.25-26.771-16.421-63.5-23.42-93.5-26.25-12-74-77-130-152-133-39-120-212-129-264-15-54.084-13.075-106.753,9.173-138.488,48.9-31.734-39.726-84.4-61.974-138.487-48.9-52-114-225-105-264,15a162.027,162.027,0,0,0-103.147,43.044c-30.633-45.365-87.1-72.091-145.206-58.044-52-114-225-105-264,15-75,3-140,59-152,133-53,5-127,23-130,83-2,42,35,72,70,86,49,20,106,18,157,5a165.625,165.625,0,0,0,120,0c47,94,178,113,251,33,61.112,8.015,113.854-5.72,150.492-29.764a165.62,165.62,0,0,0,110.861-3.236c47,94,178,113,251,33,31.385,4.116,60.563,2.495,86.487-3.311,25.924,5.806,55.1,7.427,86.488,3.311,73,80,204,61,251-33a165.625,165.625,0,0,0,120,0c51,13,108,15,157-5a147.188,147.188,0,0,0,33.5-18.694,147.217,147.217,0,0,0,33.5,18.694c49,20,106,18,157,5a165.625,165.625,0,0,0,120,0c47,94,178,113,251,33C2446.709,1093.793,2554.709,922.793,2379.709,863.793Z\" transform=\"translate(142.69 -634.312)\" fill=\"#eee\"/>\n  </svg>\n\n</div>\n\n\n\n\n<router-outlet></router-outlet>");

/***/ }),

/***/ "XVuY":
/*!**************************************************!*\
  !*** ./src/app/tree/tree-context.component.scss ***!
  \**************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = (".contextmenu {\n  position: absolute;\n  background-color: whitesmoke;\n}\n\n.menulist {\n  margin-top: 0px;\n  margin-bottom: 0px;\n  padding-left: 10px;\n}");

/***/ }),

/***/ "ZAI4":
/*!*******************************!*\
  !*** ./src/app/app.module.ts ***!
  \*******************************/
/*! exports provided: AppModule */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "AppModule", function() { return AppModule; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "mrSG");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "fXoL");
/* harmony import */ var _angular_platform_browser__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/platform-browser */ "jhN1");
/* harmony import */ var _ngrx_store__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @ngrx/store */ "l7P3");
/* harmony import */ var _ngrx_effects__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @ngrx/effects */ "9jGm");
/* harmony import */ var _reducer_index__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./reducer.index */ "g1As");
/* harmony import */ var _app_routing_module__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./app-routing.module */ "vY5A");
/* harmony import */ var _app_component__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./app.component */ "Sy1n");
/* harmony import */ var _xyz_xyz_component__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./xyz/xyz.component */ "w3p8");
/* harmony import */ var _tree_tree_component__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./tree/tree.component */ "mRMX");
/* harmony import */ var _tree_tree_node_component__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./tree/tree-node.component */ "1YIm");
/* harmony import */ var _tree_tree_context_component__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ./tree/tree-context.component */ "x/+R");
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! @angular/common/http */ "IheW");
/* harmony import */ var _tree_ngrx_tree_effects__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! ./tree/ngrx/tree.effects */ "sE2g");














let AppModule = class AppModule {
};
AppModule = Object(tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"])([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["NgModule"])({
        declarations: [
            _app_component__WEBPACK_IMPORTED_MODULE_7__["AppComponent"],
            _xyz_xyz_component__WEBPACK_IMPORTED_MODULE_8__["XyzComponent"],
            _tree_tree_component__WEBPACK_IMPORTED_MODULE_9__["TreeComponent"],
            _tree_tree_node_component__WEBPACK_IMPORTED_MODULE_10__["TreeNodeComponent"],
            _tree_tree_context_component__WEBPACK_IMPORTED_MODULE_11__["TreeContextComponent"],
        ],
        imports: [
            _angular_platform_browser__WEBPACK_IMPORTED_MODULE_2__["BrowserModule"],
            _angular_common_http__WEBPACK_IMPORTED_MODULE_12__["HttpClientModule"],
            _app_routing_module__WEBPACK_IMPORTED_MODULE_6__["AppRoutingModule"],
            _ngrx_store__WEBPACK_IMPORTED_MODULE_3__["StoreModule"].forRoot(_reducer_index__WEBPACK_IMPORTED_MODULE_5__["reducers"]),
            _ngrx_effects__WEBPACK_IMPORTED_MODULE_4__["EffectsModule"].forRoot([_tree_ngrx_tree_effects__WEBPACK_IMPORTED_MODULE_13__["TreeEffects"]]),
        ],
        providers: [],
        bootstrap: [_app_component__WEBPACK_IMPORTED_MODULE_7__["AppComponent"]]
    })
], AppModule);



/***/ }),

/***/ "e8yp":
/*!****************************************!*\
  !*** ./src/app/xyz/xyz.component.scss ***!
  \****************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = ("");

/***/ }),

/***/ "eq6X":
/*!*************************************************************************************!*\
  !*** ./node_modules/raw-loader/dist/cjs.js!./src/app/tree/tree-node.component.html ***!
  \*************************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = ("<!-- <div *ngFor=\"let node of nodes; trackBy:identify\" >\r\n  uuid: {{node.uuid}}\r\n  name: {{node.name}}\r\n  <tree-node *ngIf=\"node.children.length>0\" [nodes]=node.children></tree-node>\r\n</div> -->\r\n<div>\r\n\r\n  <div [style.clear]=\"'both'\" >\r\n    <!-- dropdown or checkbox icon -->\r\n    <div [style.float]=\"'left'\">\r\n      <div *ngIf=\"node.children.length>0; then parentNode else leafNode\"></div>\r\n      <ng-template #parentNode>\r\n        <span class=\"caret\" [ngClass]=\"{'right': !node.selected, 'down': !!node.selected}\" (click)=\"checkboxChange()\"></span>\r\n      </ng-template>\r\n      <ng-template #leafNode>\r\n        <input class=\"checkbox\" type=\"checkbox\" [checked]=\"node.selected\" (change)=\"checkboxChange()\"/>\r\n      </ng-template>\r\n    </div>\r\n    \r\n    <!-- node name -->\r\n    <div [style.float]=\"'left'\" (contextmenu)=\"this.cutomContextMenu.emit({event: $event, uuid: node.uuid})\">\r\n      {{node.name}}\r\n    </div>\r\n  </div>\r\n  \r\n  <!-- child nodes -->\r\n  <div [hidden]=\"!node.selected\" >\r\n    <div *ngFor=\"let child of node.children\" [style.padding-left]=\"'10px'\">\r\n      <tree-node [node]=\"child\" [statusUpdate]=\"statusUpdate\" (cutomContextMenu)=\"this.cutomContextMenu.emit($event)\"></tree-node>\r\n    </div>\r\n  </div>\r\n\r\n</div>\r\n");

/***/ }),

/***/ "fLOk":
/*!********************************************************************************!*\
  !*** ./node_modules/raw-loader/dist/cjs.js!./src/app/tree/tree.component.html ***!
  \********************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = ("<div [style.border]=\"'1px solid black'\">\r\n\r\n  <!-- Context menu -->\r\n  <div *ngIf=\"!!contextmenuOn\">\r\n    <tree-contextmenu [x]=\"contextmenuX\" [y]=\"contextmenuY\" \r\n      [uuid]=\"contextuuid\" [menuItems]=\"contextmenuList\" [contextNode]=\"contextNode\" \r\n      (onChoice)=\"onContextChosen($event)\">\r\n    </tree-contextmenu>\r\n  </div>\r\n\r\n  <!-- Tree Nodes -->\r\n  <div *ngIf=\"!!data\" (click)=\"disableContextMenu()\" oncontextmenu=\"return false;\">\r\n    <tree-node [node]=\"data\" [statusUpdate]=\"childStatusUpdate.asObservable() \" (cutomContextMenu)=\"onrightClick($event)\"></tree-node>\r\n  </div>\r\n</div>\r\n\r\n");

/***/ }),

/***/ "g1As":
/*!**********************************!*\
  !*** ./src/app/reducer.index.ts ***!
  \**********************************/
/*! exports provided: reducers */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "reducers", function() { return reducers; });
/* harmony import */ var _tree_ngrx_tree_reducer__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./tree/ngrx/tree.reducer */ "/7gl");

const reducers = {
    'TreeState': _tree_ngrx_tree_reducer__WEBPACK_IMPORTED_MODULE_0__["reducer"],
};


/***/ }),

/***/ "h5U3":
/*!****************************************************************************************!*\
  !*** ./node_modules/raw-loader/dist/cjs.js!./src/app/tree/tree-context.component.html ***!
  \****************************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = ("<!-- <div class=\"contextmenu\" [ngStyle]=\"{'left.px': x, 'top.px': y}\">\r\n  this is your contextmenu content\r\n</div> -->\r\n\r\n<div class=\"contextmenu\" [ngStyle]=\"{'left.px': x, 'top.px': y}\">\r\n  <ul class=\"list-group menulist\">\r\n    <li class=\"list-group-item\" *ngFor=\"let menuItem of menuItems\" \r\n        (click)=\"onChoice.emit({choice: menuItem, uuid: this.uuid, node: contextNode})\">\r\n      <span>{{ menuItem }}</span>\r\n    </li>\r\n  </ul>\r\n</div>");

/***/ }),

/***/ "mRMX":
/*!****************************************!*\
  !*** ./src/app/tree/tree.component.ts ***!
  \****************************************/
/*! exports provided: TreeComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "TreeComponent", function() { return TreeComponent; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "mrSG");
/* harmony import */ var _raw_loader_tree_component_html__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! raw-loader!./tree.component.html */ "fLOk");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/core */ "fXoL");
/* harmony import */ var _ngrx_store__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @ngrx/store */ "l7P3");
/* harmony import */ var rxjs__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! rxjs */ "qCKp");
/* harmony import */ var rxjs_operators__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! rxjs/operators */ "kU1M");
/* harmony import */ var lodash__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! lodash */ "LvDl");
/* harmony import */ var lodash__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(lodash__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _ngrx_tree_actions__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./ngrx/tree.actions */ "Nj3k");
/* harmony import */ var _ngrx_tree_reducer__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./ngrx/tree.reducer */ "/7gl");
/* harmony import */ var _node_model__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./node.model */ "uO6X");











let TreeComponent = class TreeComponent {
    constructor(store, cdr) {
        this.store = store;
        this.cdr = cdr;
        this.data = null;
        this.childStatusUpdate = new rxjs__WEBPACK_IMPORTED_MODULE_4__["Subject"]();
        this.contextmenuOn = false;
        this.contextmenuX = 0;
        this.contextmenuY = 0;
        this.contextmenuList = ['...'];
        this.contextuuid = '';
        this.contextNode = null;
        this.destroy$ = new rxjs__WEBPACK_IMPORTED_MODULE_4__["Subject"]();
    }
    ngOnInit() {
        //@ts-expect-error accessing window
        window['TreeComponent'] = this;
        //@ts-expect-error accessing window
        window['node'] = _node_model__WEBPACK_IMPORTED_MODULE_9__["NodeModel"];
        this.store.select(_ngrx_tree_reducer__WEBPACK_IMPORTED_MODULE_8__["selectTreeState"]).pipe(Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_5__["takeUntil"])(this.destroy$)).subscribe((state) => {
            switch (state.type) {
                case _ngrx_tree_actions__WEBPACK_IMPORTED_MODULE_7__["TreeActionTypes"].SetData:
                    console.log('data set', state.data);
                    this.data = lodash__WEBPACK_IMPORTED_MODULE_6__["cloneDeep"](state.data);
                    this.cdr.detectChanges();
                    break;
                case _ngrx_tree_actions__WEBPACK_IMPORTED_MODULE_7__["TreeActionTypes"].ResetData:
                    console.log('daata reset');
                    this.data = lodash__WEBPACK_IMPORTED_MODULE_6__["cloneDeep"](state.data);
                    this.cdr.detectChanges();
                    break;
                case _ngrx_tree_actions__WEBPACK_IMPORTED_MODULE_7__["TreeActionTypes"].SetAllSelected:
                    this.onSetAllSelected(lodash__WEBPACK_IMPORTED_MODULE_6__["cloneDeep"](state.payload));
                    break;
                case _ngrx_tree_actions__WEBPACK_IMPORTED_MODULE_7__["TreeActionTypes"].SelectItem:
                    console.log(state.payload);
                    break;
                case _ngrx_tree_actions__WEBPACK_IMPORTED_MODULE_7__["TreeActionTypes"].GetHTTPAttempted:
                case _ngrx_tree_actions__WEBPACK_IMPORTED_MODULE_7__["TreeActionTypes"].GetHTTPSuccessful:
                    console.log(state.type, state.payload);
                    break;
            }
        });
        const dispatch = (api, d) => { this.store.dispatch(new _ngrx_tree_actions__WEBPACK_IMPORTED_MODULE_7__["GetHTTPAttempted"]({ api: api, data: d })); };
        dispatch('api/tree/2/3', { a: 'b' });
        window['dis'] = dispatch;
    }
    onSetAllSelected(uuids) {
        const update = new _node_model__WEBPACK_IMPORTED_MODULE_9__["NodeStatusUpdate"]();
        uuids.forEach(uuid => update.states.set(uuid, true));
        update.defaultState = false;
        this.childStatusUpdate.next(update);
    }
    createDepthN(name, arr) {
        const root = new _node_model__WEBPACK_IMPORTED_MODULE_9__["NodeModel"](name);
        if (Array.isArray(arr)) {
            root.children = arr.map((len, i) => this.createDepthN(name + '_' + i, len));
        }
        else if (Number.isInteger(arr)) {
            root.children = Array(arr).fill(0).map((_, i) => new _node_model__WEBPACK_IMPORTED_MODULE_9__["NodeModel"](name + '_' + i));
        }
        return root;
    }
    SetAllSelected(uuids) {
        this.store.dispatch(new _ngrx_tree_actions__WEBPACK_IMPORTED_MODULE_7__["SetAllSelected"](uuids));
    }
    setData(data) {
        this.store.dispatch(new _ngrx_tree_actions__WEBPACK_IMPORTED_MODULE_7__["SetData"](data));
    }
    resetData() {
        this.store.dispatch(new _ngrx_tree_actions__WEBPACK_IMPORTED_MODULE_7__["ResetData"]());
    }
    //activates the menu with the coordinates
    onrightClick(event) {
        this.contextmenuX = event.event['layerX'];
        this.contextmenuY = event.event['layerY'];
        this.contextuuid = event.uuid;
        this.contextmenuList = ['...'];
        this.contextNode = null;
        this.contextmenuOn = true;
        this.cdr.detectChanges();
        this.setupContextList(event.uuid);
    }
    //disables the menu
    disableContextMenu() {
        this.contextmenuOn = false;
        this.cdr.detectChanges();
    }
    setupContextList(uuid) {
        const find = (n, uuid) => {
            if (n.uuid == uuid)
                return n;
            for (const node of n.children) {
                const found = find(node, uuid);
                if (!!found)
                    return found;
            }
            return null;
        };
        const result = find(this.data, uuid);
        this.contextNode = result;
        if (!result) {
            this.contextmenuList = ['...'];
        }
        else if (result.children.length == 0) {
            this.contextmenuList = [result.name, 'SELECT'];
        }
        else {
            this.contextmenuList = [result.name, 'SELECT ALL'];
        }
        this.cdr.detectChanges();
    }
    onContextChosen(event) {
        console.log(event.choice, 'on', event.uuid, 'node', event.node);
        const update = new _node_model__WEBPACK_IMPORTED_MODULE_9__["NodeStatusUpdate"]();
        if (event.node.children.length == 0) {
            update.states.set(event.node.uuid, !event.node.selected);
        }
        else {
            event.node.children.forEach(n => update.states.set(n.uuid, true));
        }
        this.childStatusUpdate.next(update);
        this.disableContextMenu();
    }
    ngOnDestroy() {
        this.destroy$.next();
        this.destroy$.complete();
    }
};
TreeComponent.ctorParameters = () => [
    { type: _ngrx_store__WEBPACK_IMPORTED_MODULE_3__["Store"] },
    { type: _angular_core__WEBPACK_IMPORTED_MODULE_2__["ChangeDetectorRef"] }
];
TreeComponent = Object(tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"])([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_2__["Component"])({
        selector: 'tree-comp',
        template: _raw_loader_tree_component_html__WEBPACK_IMPORTED_MODULE_1__["default"],
    })
], TreeComponent);



/***/ }),

/***/ "sE2g":
/*!*******************************************!*\
  !*** ./src/app/tree/ngrx/tree.effects.ts ***!
  \*******************************************/
/*! exports provided: TreeEffects */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "TreeEffects", function() { return TreeEffects; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "mrSG");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "fXoL");
/* harmony import */ var _ngrx_effects__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @ngrx/effects */ "9jGm");
/* harmony import */ var rxjs__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! rxjs */ "qCKp");
/* harmony import */ var rxjs_operators__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! rxjs/operators */ "kU1M");
/* harmony import */ var _tree_actions__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./tree.actions */ "Nj3k");
/* harmony import */ var _tree_services__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./tree.services */ "U2VC");







let TreeEffects = class TreeEffects {
    constructor(actions$, service) {
        this.actions$ = actions$;
        this.service = service;
        this.loadMovies$ = Object(_ngrx_effects__WEBPACK_IMPORTED_MODULE_2__["createEffect"])(() => this.actions$.pipe(Object(_ngrx_effects__WEBPACK_IMPORTED_MODULE_2__["ofType"])(_tree_actions__WEBPACK_IMPORTED_MODULE_5__["TreeActionTypes"].GetHTTPAttempted), Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_4__["switchMap"])((action) => this.service.getAll(action.payload)
            .pipe(Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_4__["map"])(result => {
            console.log(result);
            return new _tree_actions__WEBPACK_IMPORTED_MODULE_5__["GetHTTPSuccessful"]();
        }), Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_4__["catchError"])(() => rxjs__WEBPACK_IMPORTED_MODULE_3__["EMPTY"])))));
    }
};
TreeEffects.ctorParameters = () => [
    { type: _ngrx_effects__WEBPACK_IMPORTED_MODULE_2__["Actions"] },
    { type: _tree_services__WEBPACK_IMPORTED_MODULE_6__["TreeService"] }
];
TreeEffects = Object(tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"])([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Injectable"])()
], TreeEffects);



/***/ }),

/***/ "uO6X":
/*!************************************!*\
  !*** ./src/app/tree/node.model.ts ***!
  \************************************/
/*! exports provided: NodeModel, NodeStatusUpdate */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "NodeModel", function() { return NodeModel; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "NodeStatusUpdate", function() { return NodeStatusUpdate; });
class NodeModel {
    constructor(name = '', children = []) {
        this.uuid = createUUID();
        this.selected = false;
        this.name = name;
        this.children = children;
    }
}
class NodeStatusUpdate {
    constructor() {
        this.states = new Map();
    }
}
function createUUID() {
    const S4 = () => Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
    // const guid = `${S4()}${S4()}-${S4()}-${S4()}-${S4()}-${S4()}${S4()}${S4()}`;
    const guid = S4() + S4() + '-' +
        S4() + '-' +
        S4() + '-' +
        S4() + S4() + S4() + S4();
    return guid.toLowerCase();
}


/***/ }),

/***/ "vY5A":
/*!***************************************!*\
  !*** ./src/app/app-routing.module.ts ***!
  \***************************************/
/*! exports provided: AppRoutingModule */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "AppRoutingModule", function() { return AppRoutingModule; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "mrSG");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "fXoL");
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/router */ "tyNb");



const routes = [];
let AppRoutingModule = class AppRoutingModule {
};
AppRoutingModule = Object(tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"])([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["NgModule"])({
        imports: [_angular_router__WEBPACK_IMPORTED_MODULE_2__["RouterModule"].forRoot(routes)],
        exports: [_angular_router__WEBPACK_IMPORTED_MODULE_2__["RouterModule"]]
    })
], AppRoutingModule);



/***/ }),

/***/ "w3p8":
/*!**************************************!*\
  !*** ./src/app/xyz/xyz.component.ts ***!
  \**************************************/
/*! exports provided: XyzComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "XyzComponent", function() { return XyzComponent; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "mrSG");
/* harmony import */ var _raw_loader_xyz_component_html__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! raw-loader!./xyz.component.html */ "7LWo");
/* harmony import */ var _xyz_component_scss__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./xyz.component.scss */ "e8yp");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/core */ "fXoL");




let XyzComponent = class XyzComponent {
    constructor() { }
    ngOnInit() {
    }
    testfunc(n) {
    }
};
XyzComponent.ctorParameters = () => [];
XyzComponent = Object(tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"])([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_3__["Component"])({
        selector: 'app-xyz',
        template: _raw_loader_xyz_component_html__WEBPACK_IMPORTED_MODULE_1__["default"],
        styles: [_xyz_component_scss__WEBPACK_IMPORTED_MODULE_2__["default"]]
    })
], XyzComponent);



/***/ }),

/***/ "x/+R":
/*!************************************************!*\
  !*** ./src/app/tree/tree-context.component.ts ***!
  \************************************************/
/*! exports provided: TreeContextComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "TreeContextComponent", function() { return TreeContextComponent; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "mrSG");
/* harmony import */ var _raw_loader_tree_context_component_html__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! raw-loader!./tree-context.component.html */ "h5U3");
/* harmony import */ var _tree_context_component_scss__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./tree-context.component.scss */ "XVuY");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/core */ "fXoL");




let TreeContextComponent = class TreeContextComponent {
    constructor() {
        this.x = 0;
        this.y = 0;
        this.uuid = '';
        this.contextNode = null;
        this.menuItems = ['...'];
        this.onChoice = new _angular_core__WEBPACK_IMPORTED_MODULE_3__["EventEmitter"]();
    }
};
TreeContextComponent.ctorParameters = () => [];
TreeContextComponent.propDecorators = {
    x: [{ type: _angular_core__WEBPACK_IMPORTED_MODULE_3__["Input"] }],
    y: [{ type: _angular_core__WEBPACK_IMPORTED_MODULE_3__["Input"] }],
    uuid: [{ type: _angular_core__WEBPACK_IMPORTED_MODULE_3__["Input"] }],
    contextNode: [{ type: _angular_core__WEBPACK_IMPORTED_MODULE_3__["Input"] }],
    menuItems: [{ type: _angular_core__WEBPACK_IMPORTED_MODULE_3__["Input"] }],
    onChoice: [{ type: _angular_core__WEBPACK_IMPORTED_MODULE_3__["Output"] }]
};
TreeContextComponent = Object(tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"])([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_3__["Component"])({
        selector: 'tree-contextmenu',
        template: _raw_loader_tree_context_component_html__WEBPACK_IMPORTED_MODULE_1__["default"],
        styles: [_tree_context_component_scss__WEBPACK_IMPORTED_MODULE_2__["default"]]
    })
], TreeContextComponent);



/***/ }),

/***/ "ynWL":
/*!************************************!*\
  !*** ./src/app/app.component.scss ***!
  \************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = ("@charset \"UTF-8\";\n:host {\n  font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif, \"Apple Color Emoji\", \"Segoe UI Emoji\", \"Segoe UI Symbol\";\n  font-size: 14px;\n  color: #333;\n  box-sizing: border-box;\n  -webkit-font-smoothing: antialiased;\n  -moz-osx-font-smoothing: grayscale;\n}\nh1,\nh2,\nh3,\nh4,\nh5,\nh6 {\n  margin: 8px 0;\n}\np {\n  margin: 0;\n}\n.spacer {\n  flex: 1;\n}\n.toolbar {\n  position: absolute;\n  top: 0;\n  left: 0;\n  right: 0;\n  height: 60px;\n  display: flex;\n  align-items: center;\n  background-color: #1976d2;\n  color: white;\n  font-weight: 600;\n}\n.toolbar img {\n  margin: 0 16px;\n}\n.toolbar #twitter-logo {\n  height: 40px;\n  margin: 0 16px;\n}\n.toolbar #twitter-logo:hover {\n  opacity: 0.8;\n}\n.content {\n  display: flex;\n  margin: 82px auto 32px;\n  padding: 0 16px;\n  max-width: 960px;\n  flex-direction: column;\n  align-items: center;\n}\nsvg.material-icons {\n  height: 24px;\n  width: auto;\n}\nsvg.material-icons:not(:last-child) {\n  margin-right: 8px;\n}\n.card svg.material-icons path {\n  fill: #888;\n}\n.card-container {\n  display: flex;\n  flex-wrap: wrap;\n  justify-content: center;\n  margin-top: 16px;\n}\n.card {\n  border-radius: 4px;\n  border: 1px solid #eee;\n  background-color: #fafafa;\n  height: 40px;\n  width: 200px;\n  margin: 0 8px 16px;\n  padding: 16px;\n  display: flex;\n  flex-direction: row;\n  justify-content: center;\n  align-items: center;\n  transition: all 0.2s ease-in-out;\n  line-height: 24px;\n}\n.card-container .card:not(:last-child) {\n  margin-right: 0;\n}\n.card.card-small {\n  height: 16px;\n  width: 168px;\n}\n.card-container .card:not(.highlight-card) {\n  cursor: pointer;\n}\n.card-container .card:not(.highlight-card):hover {\n  transform: translateY(-3px);\n  box-shadow: 0 4px 17px rgba(0, 0, 0, 0.35);\n}\n.card-container .card:not(.highlight-card):hover .material-icons path {\n  fill: #696767;\n}\n.card.highlight-card {\n  background-color: #1976d2;\n  color: white;\n  font-weight: 600;\n  border: none;\n  width: auto;\n  min-width: 30%;\n  position: relative;\n}\n.card.card.highlight-card span {\n  margin-left: 60px;\n}\nsvg#rocket {\n  width: 80px;\n  position: absolute;\n  left: -10px;\n  top: -24px;\n}\nsvg#rocket-smoke {\n  height: calc(100vh - 95px);\n  position: absolute;\n  top: 10px;\n  right: 180px;\n  z-index: -10;\n}\na,\na:visited,\na:hover {\n  color: #1976d2;\n  text-decoration: none;\n}\na:hover {\n  color: #125699;\n}\n.terminal {\n  position: relative;\n  width: 80%;\n  max-width: 600px;\n  border-radius: 6px;\n  padding-top: 45px;\n  margin-top: 8px;\n  overflow: hidden;\n  background-color: #0f0f10;\n}\n.terminal::before {\n  content: \"•••\";\n  position: absolute;\n  top: 0;\n  left: 0;\n  height: 4px;\n  background: #3a3a3a;\n  color: #c2c3c4;\n  width: 100%;\n  font-size: 2rem;\n  line-height: 0;\n  padding: 14px 0;\n  text-indent: 4px;\n}\n.terminal pre {\n  font-family: SFMono-Regular, Consolas, Liberation Mono, Menlo, monospace;\n  color: white;\n  padding: 0 1rem 1rem;\n  margin: 0;\n}\n.circle-link {\n  height: 40px;\n  width: 40px;\n  border-radius: 40px;\n  margin: 8px;\n  background-color: white;\n  border: 1px solid #eeeeee;\n  display: flex;\n  justify-content: center;\n  align-items: center;\n  cursor: pointer;\n  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);\n  transition: 1s ease-out;\n}\n.circle-link:hover {\n  transform: translateY(-0.25rem);\n  box-shadow: 0px 3px 15px rgba(0, 0, 0, 0.2);\n}\nfooter {\n  margin-top: 8px;\n  display: flex;\n  align-items: center;\n  line-height: 20px;\n}\nfooter a {\n  display: flex;\n  align-items: center;\n}\n.github-star-badge {\n  color: #24292e;\n  display: flex;\n  align-items: center;\n  font-size: 12px;\n  padding: 3px 10px;\n  border: 1px solid rgba(27, 31, 35, 0.2);\n  border-radius: 3px;\n  background-image: linear-gradient(-180deg, #fafbfc, #eff3f6 90%);\n  margin-left: 4px;\n  font-weight: 600;\n  font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol;\n}\n.github-star-badge:hover {\n  background-image: linear-gradient(-180deg, #f0f3f6, #e6ebf1 90%);\n  border-color: rgba(27, 31, 35, 0.35);\n  background-position: -0.5em;\n}\n.github-star-badge .material-icons {\n  height: 16px;\n  width: 16px;\n  margin-right: 4px;\n}\nsvg#clouds {\n  position: fixed;\n  bottom: -160px;\n  left: -230px;\n  z-index: -10;\n  width: 1920px;\n}\n/* Responsive Styles */\n@media screen and (max-width: 767px) {\n  .card-container > *:not(.circle-link),\n.terminal {\n    width: 100%;\n  }\n\n  .card:not(.highlight-card) {\n    height: 16px;\n    margin: 8px 0;\n  }\n\n  .card.highlight-card span {\n    margin-left: 72px;\n  }\n\n  svg#rocket-smoke {\n    right: 120px;\n    transform: rotate(-5deg);\n  }\n}\n@media screen and (max-width: 575px) {\n  svg#rocket-smoke {\n    display: none;\n    visibility: hidden;\n  }\n}");

/***/ }),

/***/ "zUnb":
/*!*********************!*\
  !*** ./src/main.ts ***!
  \*********************/
/*! no exports provided */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ "fXoL");
/* harmony import */ var _angular_platform_browser_dynamic__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/platform-browser-dynamic */ "a3Wg");
/* harmony import */ var _app_app_module__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./app/app.module */ "ZAI4");
/* harmony import */ var _environments_environment__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./environments/environment */ "AytR");




if (_environments_environment__WEBPACK_IMPORTED_MODULE_3__["environment"].production) {
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["enableProdMode"])();
}
Object(_angular_platform_browser_dynamic__WEBPACK_IMPORTED_MODULE_1__["platformBrowserDynamic"])().bootstrapModule(_app_app_module__WEBPACK_IMPORTED_MODULE_2__["AppModule"])
    .catch(err => console.error(err));


/***/ }),

/***/ "zn8P":
/*!******************************************************!*\
  !*** ./$$_lazy_route_resource lazy namespace object ***!
  \******************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

function webpackEmptyAsyncContext(req) {
	// Here Promise.resolve().then() is used instead of new Promise() to prevent
	// uncaught exception popping up in devtools
	return Promise.resolve().then(function() {
		var e = new Error("Cannot find module '" + req + "'");
		e.code = 'MODULE_NOT_FOUND';
		throw e;
	});
}
webpackEmptyAsyncContext.keys = function() { return []; };
webpackEmptyAsyncContext.resolve = webpackEmptyAsyncContext;
module.exports = webpackEmptyAsyncContext;
webpackEmptyAsyncContext.id = "zn8P";

/***/ })

},[[0,"runtime","vendor"]]]);