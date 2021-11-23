class BaseMovil
{
    constructor (name = "botin")
    {
        this.name = name;
        this._x = [0.0, 0.0, 0.0];
        this._t = 0.0;
        this._u = [0.0, 0.0];
        this._u_max = [1.0, 1.0];
        this._Ts = 0.01;
        this._step_size = this._Ts;
        this._t0 = 0;
        this._tf = this.t_0 + this._step_size;
        this._Nsamples = 10+1;
        this._tX = linspace(this._t0, this._tf, this._Nsamples);

        // Model Parameters
        this._m = 2.0;
        this._r = 0.04;
        this._l = par.robot.height;
        this._w = par.robot.width;
        this._c = 1.0;
        this._b = 1.0;
        this._j = this._m * ( Math.pow(this._l, 2) + Math.pow(this._w, 2)) / 12;
        this._ce = 0.5;

        // Restrictions
        this.x_max = par.field.width - Math.max((this._l, this._w));
        this.y_max = par.field.width - Math.max((this._l, this._w));
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
            {
                u[k] = this._u_max[k] * Math.sign(u[k]);
            }
        this._u = u;
        }
    }


    Model(t, x, u)
    {
        xdot = [
            this._x[3]*cos(this._x[2]), 
            this._x[3]*sin(this._x[2]), 
            this._x[4], 
            ((this._u[0]+this._u[1])/this._r-this._c*this._x[3])/this._m, 
            (this._w*(this._u[0]-this._u[1])/(2*this._r)-this._b*this._x[4])/this._j];
        return xdot;
    }

    UpdateState()
    {
        x0 = this._x;
        var x = ODE(Model);
        this._x = x;
        this._t = this._t + this._Ts;
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
