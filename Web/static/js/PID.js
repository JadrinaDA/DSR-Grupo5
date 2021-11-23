class MobileBasePID
{
    constructor(mobile_base, reference, kp_l=0, kd_l=0, ki_l=0, kp_a=0, kd_a=0, ki_a=0, error=[0.0, 0.0], past_error=[0.0, 0.0], ac_error=[0.0, 0.0]) {
        this.kp_l = kp_l;
        this.kd_l = kd_l;
        this.ki_l = ki_l;
        this.kp_a = kp_a;
        this.kd_a = kd_a;
        this.ki_a = ki_a;
        this.error = error;
        this.past_error = past_error;
        this.ac_error = ac_error;
        this.mobile_base = mobile_base;
        this.reference = reference;

        this.max_ac_error = [2.0 , 4.0];
    }

    SetLinearConstants(kp, kd, ki){
        this.kp_l = kp;
        this.kd_l = kd;
        this.ki_l = ki;
    }

    SetAngularConstants(kp, kd, ki){
        this.kp_a = kp;
        this.kd_a = kd;
        this.ki_a = ki;
    }

    UpdateError(){
        this.past_error = this.error;

        var state = this.mobile_base.GetSensor();

        var ref = this.reference;
        //d = np.linalg.norm(ref-state[0:2])
        var d_vec = VpV(ref,SxV(-1, state.slice(0,2)) ); 
        
        // console.log(`Estado: ${state}`);
        // console.log(`Referencia: ${ref}`);

        // console.log("d:" + d_vec); //

        var d = Math.sqrt(Math.pow(d_vec[0],2) + Math.pow(d_vec[1],2));

        // console.log(ref[0]-state[0]); //
        // console.log(ref[1]-state[1]); //

        var a = state[2] - Math.PI / 2 + Math.atan2(ref[0]-state[0],ref[1]-state[1]);
        // console.log("a:" + a); //

        while (a>Math.PI){
            a = a - 2*Math.PI;
        }
        while (a<-Math.PI){
            a = a + 2*Math.PI;
        }
        
        this.error = [d,a];

        this.ac_error = VpV(this.ac_error, SxV(this.mobile_base._Ts, this.error));

        for (let k = 0; k<2; k++){
            if (Math.abs(this.ac_error[k]) > this.max_ac_error[k])
            {
                this.ac_error[k] = this.max_ac_error[k] * Math.sign(this.ac_error[k]);
            }
        }
        // console.log("Error:" + this.error);
        return this.error;
    }

    Update(){
        this.UpdateError();
        // console.log(`Error: ${this.error}`);
        // console.log(`Error acumulado: ${this.ac_error}`);
        // console.log(`Error anterior: ${this.past_error}`);
        // console.log(`Ts: ${this.mobile_base._Ts}`);
        // console.log(`Error acumulado: ${this.ac_error}`);
        var u_0 = this.kp_l*this.error[0] - this.kp_a*this.error[1] + this.ki_l*this.ac_error[0]*this.mobile_base._Ts - this.ki_a*this.ac_error[1]*this.mobile_base._Ts + this.kd_l*(this.error[0]-this.past_error[0])/this.mobile_base._Ts - this.kd_a*(this.error[1]-this.past_error[1])/this.mobile_base._Ts;
        var u_1 = this.kp_l*this.error[0] + this.kp_a*this.error[1] + this.ki_l*this.ac_error[0]*this.mobile_base._Ts + this.ki_a*this.ac_error[1]*this.mobile_base._Ts + this.kd_l*(this.error[0]-this.past_error[0])/this.mobile_base._Ts + this.kd_a*(this.error[1]-this.past_error[1])/this.mobile_base._Ts;
        this.mobile_base.SetActuator([u_0,u_1]);
    }

    SetReference(x, y){
        this.reference = [x, y];
        this.ac_error = [0.0, 0.0];
        // console.log("Nueva referencia: ");
        // console.log({x,y});
    }
}