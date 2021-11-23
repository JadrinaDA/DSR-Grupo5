class BaseMovil
{
    constructor (name = "botin")
    {
        this.name = name;
        this._x = [0.0, 0.0, 0.0, 0.0, 0.0];
        this._t = 0.0;
        this._u = [0.0, 0.0];
        this._u_max = [1.0, 1.0];
        this._Ts = 0.01;
        this._step_size = this._Ts;
        this._t0 = 0;
        this._tf = this.t_0 + this._step_size;
        this._Nsamples = 10+1;
        this._tX = linspace(this._t0, this._tf, this._Nsamples);
        // this._Ts = 0.001;
        // this.ode = new ODE(this.Model);
        // this.ode.solve(1, this._Ts, this._t, this._x)

        // Model Parameters
        this._m = 2.0;
        this._r = 0.04;
        this._l = par.robot.height;
        this._w = par.robot.width;
        this._c = 1.0;
        this._b = 1.0;
        this._j = this._m * ( Math.pow(this._l, 2) + Math.pow(this._w, 2)) / 12;
        this._ce = 0.25;

        // Restrictions
        this.x_max = par.field.width - Math.max((this._l, this._w));
        this.y_max = par.field.height - Math.max((this._l, this._w));
        this.x_min = 0;
        this.y_min = 0;

    }

    SetState(x){
        this._x = x;
    }

    SetSimulationTime(T){
        this._Ts = T;
        this._step_size = this._Ts;
        this._t0 = 0;
        this._tf = this._t0 + this._step_size;
    }

    SetActuator(u){
        // console.log(`Actuador seteado: ${u}`);
        for (let k = 0; k<2; k++){
            if (Math.abs(u[k]) > this._u_max[k])
            {
                u[k] = this._u_max[k] * Math.sign(u[k]);
            }
        this._u = u;
        }
    }

    Model()
    {
        var xdot = [
            this._x[3]*Math.cos(this._x[2]), 
            this._x[3]*Math.sin(this._x[2]), 
            this._x[4], 
            ((this._u[0]+this._u[1])/this._r-this._c*this._x[3])/this._m, 
            (this._w*(this._u[0]-this._u[1])/(2*this._r)-this._b*this._x[4])/this._j];

            // console.log(`u: ${this._u}`);
            // console.log(`r: ${this._r}`);
            // console.log(`c: ${this._c}`);
            // console.log(`x: ${this._x}`);
            // console.log(`m: ${this._m}`);
            // console.log(`xdot: ${xdot}`);
        return xdot;
    }

    UpdateState()
    { 
        var x0 = this._x;
        var dx = SxV(this._Ts, this.Model());

        // console.log(`x: ${this._x}`);
        // console.log(`dx: ${dx}`);

        var x = VpV(this._x, dx);   
        // console.log(`x: ${this._x}`);
        this._x = x;
        this._t = this._t + this._Ts;
        // this.ode.solve(1, this._Ts);

        // Check state bounds
        if (this._x[0] > this.x_max){
            this._x[0] = this.x_max;
            this._x[3] = -this._x[3]*Math.cos(this._x[2])*this._ce;
        }
        if (this._x[0] < this.x_min){
            this._x[0] = this.x_min;
            this._x[3] = -this._x[3]*Math.cos(this._x[2])*this._ce;
        }

        if (this._x[1] > this.y_max){
            this._x[1] = this.y_max;
            this._x[3] = -this._x[3]*Math.sin(this._x[2])*this._ce;
        }
        if (this._x[1] < this.y_min){
            this._x[1] = this.y_min;
            this._x[3] = -this._x[3]*Math.sin(this._x[2])*this._ce;
        }

        for(var i = 0; i<5; i++)
        {
            if (Number.isNaN(this._x[i]))
            {
                this._x[i] = 0;
                console.log("NaN encontrado en "+ i);
                console.log("ce: "+ this._ce);
            }
        }
    }

    GetSensor()
    {
        return this._x;
    }
}

function linspace(a,b,n) {
    if(typeof n === "undefined") n = Math.max(Math.round(b-a)+1,1);
    if(n<2) { return n===1?[a]:[]; }
    var i,ret = Array(n);
    n--;
    for(i=n;i>=0;i--) { ret[i] = (i*b+(n-i)*a)/n; }
    return ret;
}
