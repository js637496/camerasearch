var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
import { Observable } from 'apollo-link';
var OperationQueuing = (function () {
    function OperationQueuing() {
        this.queuedRequests = [];
        this.subscriptions = {};
        this.queuedRequests = [];
    }
    OperationQueuing.prototype.enqueueRequest = function (request) {
        var _this = this;
        var requestCopy = __assign({}, request);
        requestCopy.observable =
            requestCopy.observable ||
                new Observable(function (observer) {
                    _this.queuedRequests.push(requestCopy);
                    if (typeof requestCopy.subscriber === 'undefined') {
                        requestCopy.subscriber = {};
                    }
                    requestCopy.subscriber.next = requestCopy.next || observer.next.bind(observer);
                    requestCopy.subscriber.error = requestCopy.error || observer.error.bind(observer);
                    requestCopy.subscriber.complete =
                        requestCopy.complete || observer.complete.bind(observer);
                });
        return requestCopy.observable;
    };
    OperationQueuing.prototype.consumeQueue = function () {
        var _this = this;
        this.queuedRequests.forEach(function (request) {
            var key = request.operation.toKey();
            _this.subscriptions[key] =
                request.forward(request.operation).subscribe(request.subscriber);
            return function () {
                _this.subscriptions[key].unsubscribe();
            };
        });
        this.queuedRequests = [];
    };
    return OperationQueuing;
}());
export { OperationQueuing };
//# sourceMappingURL=queuing.js.map