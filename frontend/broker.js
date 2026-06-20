class EventBroker {

    constructor() {

        this.subscribers = {};
    }

    subscribe(event, callback) {

        if(!this.subscribers[event]) {

            this.subscribers[event] = [];
        }

        this.subscribers[event].push(callback);
    }

    publish(event, data) {

        if(!this.subscribers[event]) return;

        this.subscribers[event].forEach(

            callback => callback(data)
        );
    }
}

const broker = new EventBroker();

export default broker;