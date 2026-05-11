import React from 'react';
import { CollectionCard } from '../molecules/CollectionCard';

export const CollectionGrid: React.FC = () => (
  <div className="lg:col-span-12 mt-section-gap pt-16 border-t border-primary">
    <h2 className="font-headline-lg text-headline-lg text-primary text-center mb-16 tracking-tighter">
      THE SEASONAL COLLECTION
    </h2>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter">
      <CollectionCard 
        title="APEX PLASMA MASTER"
        imageSrc="https://lh3.googleusercontent.com/aida-public/AB6AXuBVFAA4noHnfxeajEbdIvqiPR_RPHt05NnZzV4EMU13eDdLWLH8ZfbDB0v6YsBnBo7JC1Kkp1Hf5hTgzcNTO6ABdXwQTHTbUr6H4uSzg-D7lBGDdLuA6kG0N9S18BKR3WQ0RVq-0M6Xk9_BGVexjBMv12qK5pDl_ic5SE7kyFz1cnvURq9M61T4Ag-HqLnAYOXPYaeqRlIrxunFH17qhihZ1Fdv_ciGrO725_rAa6DIwM7EOfYKrIVMGajNEyaW75sn7b-A-t9XSnlc"
        imageAlt="Apex Plasma Master"
        badges={['DEGREE 100', 'CAMO THREADED']}
      />
      <CollectionCard 
        title="GLAIVE DOMINUS"
        imageSrc="https://lh3.googleusercontent.com/aida-public/AB6AXuDQabcyDabyIILsmg_4LgHCk6KTA277WvcDpGGR6QOvJ_FAY2d7ZzfnxGc4kkDMJr2_Wbp7MabxzP2f2BL420sz0bDnfA5S25bf0MGMi96iMJzZULj8B5S69C1G8oPsSzPTk0nXJqPnHzVY8lEVHI_45RKwNh3qZLqZTC_Eiz4yRK47bRhEuLTnSJ2QbiZTo8llMlTyomMcdSkVKoN9UbwLeAPXO6LoPMm2adwIHkqynl75TdOwc3aDgVm69Z0doh8FCx0NfwK82I1n"
        imageAlt="Glaive Dominus"
        badges={['LEAD-POPPING', 'PIERCE BONUS']}
      />
      <CollectionCard 
        title="NAVARCH OF THE SEAS"
        imageSrc="https://lh3.googleusercontent.com/aida-public/AB6AXuAhW1TpbQwPrZhUYSpr5mMWCcZLoEaLsm7Jh_z385PXJbn3uTnUTjWVydXUalPPpu1fPa6Oy8qB9EH3fUFG1J2MENLhfUlyoqkv7H4yPC-HyX192c5vq_lrvp4Gi1wBNso846qJsUdgMvc7DXqF8Jhi0kojyDEcdmiy9V81vj76L5EnweLoMcXy1ejLyvZYu4FleNxMJfqFUgmjJTl52XiN0bf2ImDYgQd_CpFqatXsGoI_ai34nD9DduVaJDjqNiLSMP-l99mHUtiv"
        imageAlt="Navarch of the Seas"
        badges={['DEGREE 100', 'CAMO THREADED']}
        hiddenLg={true}
      />
    </div>
  </div>
);
